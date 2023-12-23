import logging
logger = logging.getLogger(__name__)

from typing import Any, Dict, List
from dacite import from_dict
from grapycal.extension.utils import NodeInfo
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.node import Node
from grapycal.sobjects.port import InputPort, OutputPort, Port
from objectsync import SObject, SObjectSerialized
from itertools import count

class Editor(SObject):

    frontend_type = 'Editor'

    def build(self,old:SObjectSerialized|None=None):
        from grapycal.core.workspace import Workspace # avoid circular import
        self.workspace: Workspace = self._server.globals.workspace
        self.node_types = self.workspace._extention_manager._node_types_topic
        self.id_counter = count(0)
        
        if old is not None:
            # If the editor is loaded from a save, we need to recreate the nodes and edges.
            nodes : list[SObjectSerialized] = []
            edges : list[SObjectSerialized] = []
            node_types = self.node_types.get()
            for obj in old.children.values():
                if obj.type in node_types:
                    nodes.append(obj)
                elif obj.type == 'Edge':
                    edges.append(obj)
                else:
                    raise Exception(f'Unknown object type {obj.type}')
            self.restore(nodes,edges)

        # called by client
        self.register_service('create_edge',self.create_edge_from_port_id)
        self.register_service('create_node',self.create_node_service)
        self.register_service('copy',self._copy)
        self.register_service('paste',self._paste)
        self.register_service('cut',self._cut)

        # when frontend calls paste service, we need to emit the paste_wrapper event and create the nodes and edges in the callback in manual mode
        # this makes topicsync save the args of paste_wrapper in the history instead of the result of paste
        self.on('paste_wrapper',self._paste_wrapper_emitted,self._paste_wrapper_inversed,auto=False)

    def restore(self, node_list : list[SObjectSerialized], edge_list : list[SObjectSerialized]):
        
        # Generate new ids for the nodes and edges
        nodes : dict[str,SObjectSerialized] = {}
        edges : dict[str,SObjectSerialized] = {}
        for obj in node_list:
            new_id = f'r_{next(self.id_counter)}' # r means restored
            nodes[new_id] = obj

        for obj in edge_list:
            new_id = f'r_{next(self.id_counter)}'
            edges[new_id] = obj

        # Edges and nodes may reference each other with attributes, so we need to update the references
        id_map : dict[str,str] = {}
        for new_id,old in nodes.items():
            id_map[old.id] =  new_id
        for new_id,old in edges.items():
            id_map[old.id] =  new_id

        for obj in nodes.values():
            obj.update_references(id_map)
        
        for obj in edges.values():
            obj.update_references(id_map)

        # TODO: also update references of existing nodes

        # To handle edge recovery, we need to know the mapping between old and new port ids.
        # We use the port name and the node id to identify a port.
        # The mapping can be accessed by combining the following maps:
        #   port_map_1: old id -> (port name, old node id)
        #   node_id_map: old node id -> new node id
        #   port_map_2: (port name, new node id) -> new id

        port_map_1 = {}
        for node in nodes.values():
            old_port_ids: List[str] = node.get_attribute('in_ports') + node.get_attribute('out_ports')
            for old_port in old_port_ids:
                old_port_info = node.children[old_port]
                port_map_1[old_port] = (old_port_info.get_attribute('is_input'),old_port_info.get_attribute('name'),node.id)

        # Recreate the nodes
        new_nodes : dict[str,tuple[SObjectSerialized,Node]] = {}
        for obj in nodes.values():
            # Here we don't pass serialized = obj because we don't want to use the SObject._deserialize.
            # Instead we want a clean build of the node then calling restore_from_version explicitly.
            # By doing this, the node can resolve any backward compatibility issues manually.
            node = self.add_child_s(obj.type,id=id_map[obj.id]) 
            assert isinstance(node,Node), f'Expected node, got {node}'
            node.old_node_info = NodeInfo(obj)
            node.restore_from_version('',node.old_node_info)
            new_nodes[obj.id] = (obj,node)

        # After the nodes are created and before the edges are created, we must map the port ids so edges can find the ports on new nodes
        port_map_2 = {}
        for old_serialized,new_node in new_nodes.values():

            ports: List[Port] = new_node.in_ports.get() + new_node.out_ports.get() # type: ignore
            for port in ports:
                port_map_2[(port.is_input.get(),port.name.get(),new_node.get_id())] = port.get_id()

        existing_ports = []
        for node in self.get_children_of_type(Node):
            existing_ports += [port.get_id() for port in (node.in_ports.get() + node.out_ports.get())]

        existing_ports = set(existing_ports)

        def port_id_map(old_port_id:str) -> str|None:
            '''
            With port_map_1 and port_map_2, we can map old ports to new ones by matching their names
            None is returned if the port does not exist in the new editor
            '''
            
            
            try:
                is_input, port_name, old_node_id = port_map_1[old_port_id]
            except KeyError:
                # fallback to finding the existing port
                if old_port_id in existing_ports:
                    return old_port_id
                else:
                    return None
                
            new_node_id = id_map[old_node_id]

            try:
                new_port_id =  port_map_2[(is_input,port_name,new_node_id)]
            except KeyError:
                if old_port_id in existing_ports:
                    return old_port_id
                else:
                    return None

            return new_port_id
        
        # Now we can recreate the edges

        new_edge_ids = []
        for obj in edges.values():
            new_tail_id = port_id_map(obj.get_attribute('tail'))
            new_head_id = port_id_map(obj.get_attribute('head'))
            if new_tail_id is None or new_head_id is None:
                print(f'Warning: edge {obj.id} was not restored. head: {new_head_id} tail: {new_tail_id}')
                continue # skip edges that reference ports that don't exist in the new version of nodes

            # check the ports accept the edge
            tail = self._server.get_object(new_tail_id)
            head = self._server.get_object(new_head_id)
            assert isinstance(tail,OutputPort) and isinstance(head,InputPort)
            if tail.is_full() or head.is_full():
                print(f'Warning: aa edge {obj.id} was not restored. head: {new_head_id} tail: {new_tail_id}')
                continue # skip edges that reference ports that are full
            new_edge_id = self.create_edge_from_port_id(new_tail_id,new_head_id)
            new_edge_ids.append(new_edge_id)

        # return the ids of the restored nodes and edges
        new_node_ids = []
        for _,node in new_nodes.values():
            new_node_ids.append(node.get_id())

        return new_node_ids,new_edge_ids

    def create_node(self, node_type: type, **kwargs) -> Node:
        return self.add_child(node_type, is_preview=False, **kwargs)
    
    def create_node_service(self, node_type: str, **kwargs):
        self.add_child_s(node_type, is_preview=False, **kwargs)
    
    def create_edge(self, tail: OutputPort, head: InputPort) -> Edge:
        # Check the tail and head have space for the edge
        if tail.is_full() or head.is_full():
            raise Exception('A port is full')
        return self.add_child(Edge, tail=tail, head=head)
    
    def create_edge_from_port_id(self, tail_id: str, head_id: str):
        tail = self._server.get_object(tail_id)
        head = self._server.get_object(head_id)
        assert isinstance(tail, OutputPort)
        assert isinstance(head, InputPort)
        new_edge = self.create_edge(tail, head)
        return new_edge.get_id()

    def _copy(self, ids: list[str]):
        '''
        Returns a list of serialized objects
        '''

        result = {'nodes':[],'edges':[]} # type: dict[str,list[Dict[str,Any]]]

        for id in ids:
            obj = self._server.get_object(id)
            if isinstance(obj,Node):
                result['nodes'].append(obj.serialize().to_dict())
            elif isinstance(obj,Edge):
                result['edges'].append(obj.serialize().to_dict())
            else:
                raise Exception(f'Unknown object type {obj}')
            
        return result
    
    def _paste(self, data: dict[str,list[Dict]],mouse_pos: dict[str,int]):
        '''
        data is the result of _copy
        '''
        try:
            # convert the dicts to SObjectSerialized
            nodes = [from_dict(SObjectSerialized,d) for d in data['nodes']]
            edges = [from_dict(SObjectSerialized,d) for d in data['edges']]
        except Exception as e:
            logger.info(f'Invalid paste content')
            return
        
        # translate the center of the nodes to the mouse position
        def get_x(node:SObjectSerialized):
            return float(node.get_attribute('translation').split(',')[0])
        def get_y(node:SObjectSerialized):
            return float(node.get_attribute('translation').split(',')[1])
        
        x1 = min(get_x(node) for node in nodes)
        y1 = min(get_y(node) for node in nodes)
        x2 = max(get_x(node) for node in nodes)
        y2 = max(get_y(node) for node in nodes)

        dx = mouse_pos['x'] - (x1 + x2)/2
        dy = mouse_pos['y'] - (y1 + y2)/2

        for node in nodes:
            new_x = float(get_x(node)) + dx
            new_y = float(get_y(node)) + dy
            new_translation = f'{new_x},{new_y}'
            for attr in node.attributes:
                name, type, value, is_stateful, order_strict = attr
                if name == 'translation':
                    attr[2] = new_translation
                
        self.emit('paste_wrapper',nodes=nodes,edges=edges)

    def _paste_wrapper_emitted(self, nodes: list[SObjectSerialized], edges: list[SObjectSerialized],**kwargs):
        
        # restore the nodes and edges
        new_node_ids,new_edge_ids = self.restore(nodes,edges)
        return {'new_node_ids':new_node_ids,'new_edge_ids':new_edge_ids}

    def _paste_wrapper_inversed(self, new_node_ids: list[str], new_edge_ids: list[str],**kwargs):
        # the opposite of _paste_wrapper_emitted
        # we need to delete the nodes and edges that were pasted
        # this is called when undoing the paste_wrapper

        # delete the nodes and edges
        for id in new_edge_ids:
            self._server.destroy_object(id)
        for id in new_node_ids:
            self._server.destroy_object(id)


    def _cut(self, ids: list[str]):
        '''
        Returns a list of serialized objects
        '''

        result = {'nodes':[],'edges':[]} # type: dict[str,list[Dict[str,Any]]]

        edges_to_delete = [] # type: list[Edge]
        nodes_to_delete = [] # type: list[Node]
        for id in ids:
            obj = self._server.get_object(id)
            if isinstance(obj,Node):
                nodes_to_delete.append(obj)
                result['nodes'].append(obj.serialize().to_dict())
            elif isinstance(obj,Edge):
                edges_to_delete.append(obj)
                result['edges'].append(obj.serialize().to_dict())
            else:
                raise Exception(f'Unknown object type {obj}')
            
        for edge in edges_to_delete:
            edge.destroy()

        for node in nodes_to_delete:
            node.destroy()

        return result