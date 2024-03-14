import asyncio
import logging
import pkgutil

import subprocess
from unittest import skip
from grapycal.extension.extensionSearch import get_remote_extensions
from grapycal.extension.utils import get_extension_info, get_package_version, list_to_dict, snap_node
logger = logging.getLogger(__name__)

from typing import TYPE_CHECKING, Dict, List, Tuple
import sys
from os.path import join, dirname
import shutil
from grapycal.extension.extension import Extension, CommandCtx, get_extension
from grapycal.sobjects.node import Node
from grapycal.sobjects.port import Port
import objectsync

if TYPE_CHECKING:  
    from grapycal.core.workspace import Workspace

class ExtensionManager:
    def __init__(self,objectsync_server:objectsync.Server,workspace:'Workspace') -> None:
        self._objectsync = objectsync_server
        self._workspace = workspace
        cwd = sys.path[0]
        self._local_extension_dir = join(cwd,'.grapycal','extensions')
        sys.path.append(self._local_extension_dir)
        self._extensions: Dict[str, Extension] = {}

        # Use this topic to inform the client about the extensions
        self._imported_extensions_topic = self._objectsync.create_topic('imported_extensions',objectsync.DictTopic,is_stateful=False)
        self._avaliable_extensions_topic = self._objectsync.create_topic('avaliable_extensions',objectsync.DictTopic,is_stateful=False)
        self._not_installed_extensions_topic = self._objectsync.create_topic('not_installed_extensions',objectsync.DictTopic,is_stateful=False)
        self._node_types_topic = self._objectsync.create_topic('node_types',objectsync.DictTopic,is_stateful=False)
        self._objectsync.on('import_extension',self.import_extension,is_stateful=False)
        self._objectsync.on('unimport_extension',self.unimport_extension,is_stateful=False)
        self._objectsync.on('update_extension',self.update_extension,is_stateful=False)
        self._objectsync.on('refresh_extensions',self._update_available_extensions_topic,is_stateful=False)
        self._objectsync.on('install_extension',self._install_extension,is_stateful=False)

    def start(self) -> None:
        '''
        Called after the event loop is started.
        '''
        self._update_available_extensions_topic()

    def import_extension(self, extension_name: str, create_nodes=True, log=True) -> Extension:
        extension = self._load_extension(extension_name)
        if create_nodes:
            try:
                self.create_preview_nodes(extension_name)
            except Exception:
                self._unload_extension(extension_name)
                raise
            self._instantiate_singletons(extension_name)
        self._update_available_extensions_topic()
        self._workspace.slash.register(f'reload: {extension_name}',lambda _: self.update_extension(extension_name),source=extension_name)
        self._workspace.slash.register(f'unimport: {extension_name}',lambda _: self.unimport_extension(extension_name),source=extension_name)
        if log:
            logger.info(f'Imported extension {extension_name}')
            self._workspace.send_message_to_all(f'Imported extension {extension_name}')
        self._objectsync.clear_history_inclusive()
        return extension

    def update_extension(self, extension_name: str) -> None:
        old_version = self._extensions[extension_name]
        old_node_types = set(old_version.node_types_d_without_extension_name.keys())
        new_version = get_extension(extension_name,self._workspace,set(self._objectsync.get_all_node_types().values())-set(old_version.node_types_d.values()))

        # Get diff between old and new version
        new_node_types = set(new_version.node_types_d_without_extension_name.keys())
        removed_node_types = old_node_types - new_node_types
        added_node_types = new_node_types - old_node_types
        changed_node_types = old_node_types & new_node_types

        existing_nodes = self._workspace.get_workspace_object().get_children_of_type(Node)

        # Ensure there are no nodes of removed types
        for node in existing_nodes:
            type_name_without_extension = node.get_type_name().split('.')[1]
            if type_name_without_extension in removed_node_types:
                self._unload_extension(extension_name)
                raise Exception(f'Cannot update extension {extension_name} because there are still nodes of type {type_name_without_extension} in the workspace.')

        # Find nodes of changed types
        def hit(node:objectsync.SObject) -> bool:
            # Only update nodes that are not previews...
            if not isinstance(node,Node):
                return False
            if node.is_preview.get():
                return False
            
            # ... and are of the changed types.
            # Node type name format: grapycal_packagename.node_type_name
            node_type_name = node.get_type_name() 
            node_extension_name,node_type_name_without_extension = node_type_name.split('.')
            return node_extension_name == extension_name and node_type_name_without_extension in changed_node_types

        nodes_to_update = self._workspace.get_workspace_object().main_editor.top_down_search(
            accept=hit,
            stop=hit,
            type=Node
        )
        
        # Remove nodes of the changed types
        nodes_to_recover:List[objectsync.sobject.SObjectSerialized] = []
        edges_to_recover:List[objectsync.sobject.SObjectSerialized] = []
        
        for node in nodes_to_update:
            # First serialize the node
            nodes_to_recover.append(node.serialize())
            ports: List[Port] = node.in_ports.get() + node.out_ports.get() # type: ignore
            for port in ports:
                for edge in port.edges.copy():
                    edges_to_recover.append(edge.serialize())
                    self._objectsync.destroy_object(edge.get_id())

            # Then destroy the node
            self._objectsync.destroy_object(node.get_id())

        type_map = {}
        for type_name in changed_node_types:
            type_map[old_version.add_extension_name_to_node_type(type_name)] = new_version.add_extension_name_to_node_type(type_name)
            
        for node in nodes_to_recover:
            node.update_type_names(type_map)

        '''
        Now, the old nodes, ports and edges are destroyed. Their information is stored in nodes_to_recover and edges_to_recover.
        '''

        # Unimport old version
        self._destroy_nodes(old_version.name)
        self.unimport_extension(old_version.name,log=False)
        self.import_extension(new_version.name,create_nodes=False,log=False)

        self._workspace.get_workspace_object().main_editor.restore(nodes_to_recover,edges_to_recover)

        self.create_preview_nodes(new_version.name)
        self._instantiate_singletons(new_version.name)
        self._update_available_extensions_topic()

        logger.info(f'Reloaded extension {extension_name}')
        self._workspace.send_message_to_all(f'Reloaded extension {extension_name} {new_version.version}')
        self._objectsync.clear_history_inclusive()

    def unimport_extension(self, extension_name: str, log=True) -> None:
        self._check_extension_not_used(extension_name)
        self._destroy_nodes(extension_name)
        self._unload_extension(extension_name)
        self._update_available_extensions_topic()
        self._workspace.slash.unregister_source(extension_name)
        if log:
            logger.info(f'Unimported extension {extension_name}')
            self._workspace.send_message_to_all(f'Unimported extension {extension_name}')
        self._objectsync.clear_history_inclusive() 

    def _instantiate_singletons(self, extension_name: str) -> None:
        '''
        For each singleton node type, create an instance if there is none.
        '''
        extension = self._extensions[extension_name]
        for node_type_name, node_type in extension.singletonNodeTypes.items():
            if node_type._auto_instantiate and not hasattr(node_type,'instance'):
                self._workspace.get_workspace_object().main_editor.create_node(node_type, translation='9999,9999',is_new = True)

    def _update_available_extensions_topic(self) -> None:
        self._workspace.add_task_to_event_loop(self._update_available_extensions_topic_async())

    async def _update_available_extensions_topic_async(self) -> None:
        '''
        This function is async because it sends requests to get package metadata.
        '''
        available_extensions = self._scan_available_extensions()
        self._avaliable_extensions_topic.set(list_to_dict(available_extensions,'name'))
        self._workspace.slash.unregister_source('import_extension')
        for extension in available_extensions:
            extension_name = extension['name']+''
            self._workspace.slash.register(f'import: {extension_name}',lambda _,n=extension_name: self.import_extension(n),source='import_extension')
        not_installed_extensions = await get_remote_extensions()
        not_installed_extensions = [info for info in not_installed_extensions 
                                        if (info['name'] not in self._avaliable_extensions_topic and 
                                            info['name'] not in self._imported_extensions_topic)
                                    ]
        self._not_installed_extensions_topic.set(list_to_dict(not_installed_extensions,'name'))
        

    def _scan_available_extensions(self) -> list[dict]:
        '''
        Returns a list of available extensions that is importable but not imported yet.
        '''
        available_extensions = []
        for pkg in pkgutil.iter_modules():
            if  pkg.name.startswith('grapycal_') and pkg.name != 'grapycal':
                if pkg.name not in self._extensions:
                    # find pyproject.toml and get package version
                    available_extensions.append(get_extension_info(pkg.name))
        return available_extensions
    
    async def _check_extension_compatible(self, extension_name: str):
        # dry run the installation and get its output
        out = await asyncio.create_subprocess_exec('pip','install',extension_name,'--dry-run',stdout=subprocess.PIPE)
        out = await out.stdout.read()
        out = out.decode('utf-8')
        # check if the line begin with "Would install" contains "grapycal"
        package_regex = r'([^\s]*)-(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?'
        for line in out.split('\n'):
            if line.startswith('Would install'):
                # use regex to get the package name
                import re
                for match in re.findall(package_regex,line):
                    if match[0] == 'grapycal':
                        # This shows that pip will reinstall grapycal, maybe in a different version.
                        # This is not allowed when the extension is installed from the UI.
                        from importlib.metadata import version
                        cur = version('grapycal')

                        raise Exception(f'Cannot install extension {extension_name}.\n\
                            Current grapycal version:\t{cur}. \n\
                            Required grapycal version:\t{match[1]}.{match[2]}.{match[3]}.\n\
                            Please update grapycal first with "pip install --upgrade grapycal".\n\
                            If grapycal is installed in editable mode, please reinstall grapycal with "pip install -e backend"\
                            ')
        
    def _install_extension(self, extension_name: str) -> None:
        self._workspace.add_task_to_event_loop(self._install_extension_async(extension_name))
    
    async def _install_extension_async(self, extension_name: str) -> None:
        # TODO: async this slow stuff
        # check if the extension is compatible
        logger.info(f'Checking compatibility of extension {extension_name} to current Grapycal version...')
        try:
            await self._check_extension_compatible(extension_name)
        except Exception as e:
            logger.error(f'{e}')
            return
        # run pip install
        logger.info(f'Installing extension {extension_name}. This may take a while...')
        pip = await asyncio.create_subprocess_exec('pip','install',extension_name)
        await pip.wait()

        logger.info(f'Installed extension {extension_name}. Now importing...')
        # import extension
        self.import_extension(extension_name)
        # update available extensions
        await self._update_available_extensions_topic_async()

    def _load_extension(self, name: str) -> Extension:
        extension = self._extensions[name] = get_extension(name,self._workspace,set(self._objectsync.get_all_node_types().values()))
        self._register_extension(name)
        self._imported_extensions_topic.add(name,extension.get_info())
        for node_type_name, node_type in extension.node_types_d.items():
            self._node_types_topic.add(node_type_name,{
                'name':node_type_name,
                'category':node_type.category,
                'description':node_type.__doc__,
            })
        return extension
    
    def _register_extension(self, name: str) -> None:
        for node_type_name, node_type in self._extensions[name].node_types_d.items():
            self._objectsync.register(node_type,node_type_name)
            self._workspace.slash.register(
                    node_type_name.split('.')[1][:-4],
                    lambda ctx,n=node_type_name: self._create_node_slash_listener(ctx,n), # the lambda is necessary to capture the value of n
                    source=name,
                    prefix=''
                )
        for slash in self._extensions[name].get_slash_commands().values():
            self._workspace.slash.register(slash['name'],slash['callback'],source=name)

    def _create_node_slash_listener(self, ctx:CommandCtx, node_type_name: str) -> None:
        x = snap_node(ctx.mouse_pos[0])
        y = snap_node(ctx.mouse_pos[1])
        translation = [x,y]
        self._workspace.get_workspace_object().main_editor.create_node(node_type_name,translation=translation)
    
    def _check_extension_not_used(self, name: str) -> None:
        extension = self._extensions[name]
        node_types = extension.node_types_d
        skip_types = set() # skip singleton nodes with auto_instantiate=True
        for node_type in extension.singletonNodeTypes.values():
            if node_type._auto_instantiate:
                skip_types.add(extension.add_extension_name_to_node_type(node_type.__name__))

        for obj in self._workspace.get_workspace_object().main_editor.top_down_search(type=Node):
            if obj.get_type_name() not in node_types: continue
            if obj.is_preview.get(): continue
            if obj.get_type_name() in skip_types: continue
            raise Exception(f'Cannot unload extension {name}, there are still {obj.__class__.__name__} in the workspace')

    def _unload_extension(self, name: str) -> None:
        node_types = self._extensions[name].node_types_d
        for node_type in node_types:
            self._objectsync.unregister(node_type)
        self._extensions.pop(name)
        self._imported_extensions_topic.pop(name)
        for node_type_name in node_types:
            self._node_types_topic.pop(node_type_name)
            
    def create_preview_nodes(self, name: str) -> None:
        node_types = self._extensions[name].node_types_d
        for node_type in node_types.values():
            if not node_type.category == 'hidden' and not node_type._is_singleton:
                self._objectsync.create_object(node_type,parent_id=self._workspace.get_workspace_object().sidebar.get_id(),is_preview=True,is_new=True)
 
    def _destroy_nodes(self, name: str) -> None:
        node_types = self._extensions[name].node_types_d
        for obj in self._workspace.get_workspace_object().sidebar.get_children_of_type(Node)\
        + self._workspace.get_workspace_object().main_editor.top_down_search(type=Node):
            if obj.get_type_name() in node_types:
                self._objectsync.destroy_object(obj.get_id())



    def get_extension(self, name: str) -> Extension:
        return self._extensions[name]
    
    def get_extention_names(self) -> list[str]:
        return list(self._extensions.keys())
    
    def get_extensions_info(self) -> List[dict]:
        return [extension.get_info() for extension in self._extensions.values()]