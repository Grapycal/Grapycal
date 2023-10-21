from grapycal.sobjects.edge import Edge
from grapycal.sobjects.editor import Editor
from grapycal.sobjects.node import Node
from grapycal.sobjects.sidebar import Sidebar
from objectsync import SObject, ObjTopic, StringTopic, IntTopic

class WorkspaceObject(SObject):
    frontend_type = 'Workspace'
        
    def build(self):
        self.webcam = self.add_child(WebcamStream)
        self.sidebar =self.add_child(Sidebar)
        self.main_editor = self.add_child(Editor)
        self.add_attribute('main_editor',ObjTopic).set(self.main_editor)

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
            if edge.is_destroyed():
                raise Exception(f'Edge {edge} is already destroyed')
        for node in nodes:
            if node.is_destroyed():
                raise Exception(f'Node {node} is already destroyed')

        for edge in edges:
            edge.remove()
        for node in nodes:
            node.remove()

class WebcamStream(SObject):
    frontend_type = 'WebcamStream'
    def build(self):
        self.image = self.add_attribute('image',StringTopic)
        self.source_client = self.add_attribute('source_client',IntTopic,-1)

    def init(self):
        self.source_client.set(-1)
        self._server.globals.workspace.webcam = self