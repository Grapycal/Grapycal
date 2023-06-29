from typing import Any, Dict
from grapycal.sobjects.editor import Editor
from grapycal.sobjects.sidebar import Sidebar
from objectsync import SObject, ObjTopic

class WorkspaceObject(SObject):
    frontend_type = 'Workspace'
    def pre_build(self, attribute_values: Dict[str, Any] | None, **_):
        self.main_editor: ObjTopic[Editor] = self.add_attribute('main_editor',ObjTopic)
    def build(self):
        self.add_child(Sidebar)
        self.main_editor.set(self.add_child(Editor))
    def post_build(self):
        self.sidebar = self.get_child_of_type(Sidebar)