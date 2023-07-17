from typing import Any, Dict
from grapycal.sobjects.editor import Editor
from grapycal.sobjects.sidebar import Sidebar
from objectsync import SObject, ObjTopic

class WorkspaceObject(SObject):
    frontend_type = 'Workspace'
        
    def build(self):
        self.main_editor = self.add_attribute('main_editor',ObjTopic[Editor])
        self.add_child(Sidebar)
        self.main_editor.set(self.add_child(Editor))
        self.sidebar = self.get_child_of_type(Sidebar)