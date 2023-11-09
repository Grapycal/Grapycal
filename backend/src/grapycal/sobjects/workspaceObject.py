from typing import Any, Dict
from grapycal.sobjects.edge import Edge
from grapycal.sobjects.editor import Editor
from grapycal.sobjects.node import Node
from grapycal.sobjects.sidebar import Sidebar
from grapycal.sobjects.settings import Settings
from objectsync import SObject, ObjTopic, SObjectSerialized, StringTopic, IntTopic, Topic, WrappedTopic

class WorkspaceObject(SObject):
    frontend_type = 'Workspace'

    def build(self,old:SObjectSerialized|None=None):
        if old is None:
            self.settings = self.add_child(Settings)
            self.webcam = self.add_child(WebcamStream)
            self.sidebar = self.add_child(Sidebar)
            self.main_editor = self.add_child(Editor)
        else:
            if old.has_child('settings'):
                self.settings = self.add_child(Settings,old = old.get_child('settings'))
            else:
                self.settings = self.add_child(Settings)
            if old.has_child('webcam'):
                self.webcam = self.add_child(WebcamStream,old = old.get_child('webcam'))
            else:
                self.webcam = self.add_child(WebcamStream)
            self.sidebar = self.add_child(Sidebar,old = old.get_child('sidebar'))

            if old.has_child('main_editor'):
                self.main_editor = self.add_child(Editor,old = old.get_child('main_editor'))
            else:
                self.main_editor = self.add_child(Editor,old = old.children[old.get_attribute('main_editor')])
        
        # read by frontend
        self.add_attribute('main_editor',ObjTopic).set(self.main_editor)

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
    def build(self,old:SObjectSerialized|None=None):
        self.image = self.add_attribute('image',StringTopic)
        self.source_client = self.add_attribute('source_client',IntTopic,-1,is_stateful=False)

    def init(self):
        self.source_client.set(-1)
        self._server.globals.workspace.webcam = self