from typing import Any, Dict
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.editor import Editor
from grapycal.sobjects.node import Node
from grapycal.sobjects.port import Port
from grapycal.sobjects.sidebar import Sidebar
from objectsync import SObject, ObjTopic

class WorkspaceObject(SObject):
    frontend_type = 'Workspace'
        
    def build(self):
        self.main_editor = self.add_attribute('main_editor',ObjTopic[Editor])
        self.add_child(Sidebar)
        self.main_editor.set(self.add_child(Editor))
        self.sidebar = self.get_child_of_type(Sidebar)

    def init(self):
        self._server.on('delete',self._delete_callback,is_stateful=False)

    def _delete_callback(self,ids):
        nodes:set[Node] = set()
        edges:set[Edge] = set()
        for id in ids:
            obj = self._server.get_object(id)
            match obj:
                case Node():
                    nodes.add(obj)
                case Edge():
                    edges.add(obj)

        for node in nodes:
            for port in node.in_ports.get() + node.out_ports.get():
                for edge in port.edges:
                    edges.add(edge)

        for edge in edges:
            edge.remove()
        for node in nodes:
            node.remove()