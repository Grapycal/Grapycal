from grapycal.sobjects.sidebar import Sidebar
from objectsync import SObject

class WorkspaceObject(SObject):
    frontend_type = 'Workspace'
    def build(self):
        self.add_child(Sidebar)
    def post_build(self):
        self.sidebar = self.get_child_of_type(Sidebar)