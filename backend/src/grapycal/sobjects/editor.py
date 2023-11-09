from typing import List
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
            # Let the node handle the recovery
            old_node_info = NodeInfo(old_serialized)
            new_node.old_node_info = old_node_info
            new_node.restore_from_version('',old_node_info) #TODO version name

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
            if old_port_id in existing_ports:
                return old_port_id
            
            try:
                is_input, port_name, old_node_id = port_map_1[old_port_id]
            except KeyError:
                return None
            
            new_node_id = id_map[old_node_id]

            try:
                new_port_id =  port_map_2[(is_input,port_name,new_node_id)]
            except KeyError:
                return None
            
            return new_port_id
        
        # Now we can recreate the edges

        for obj in edges.values():
            new_tail_id = port_id_map(obj.get_attribute('tail'))
            new_head_id = port_id_map(obj.get_attribute('head'))
            if new_tail_id is None or new_head_id is None:
                continue # skip edges that reference ports that don't exist in the new version of nodes
            self.create_edge_from_port_id(new_tail_id,new_head_id)

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
        self.create_edge(tail, head)
