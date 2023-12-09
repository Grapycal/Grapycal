import os
from objectsync import SObject

from grapycal.utils.io import read_workspace

class FileView(SObject):
    frontend_type = 'FileView'
    def init(self):
        self.register_service('ls',self.ls)
        self.register_service('get_workspace_metadata',self.get_workspace_metadata)
        self.metadata_cache = {}

    def ls(self,path):
        # root is cwd
        root = os.getcwd()
        path = os.path.join(root,path)
        if not os.path.exists(path):
            return []
        if os.path.isfile(path):
            return []
        result = []
        for f in os.listdir(path):
            if os.path.isdir(os.path.join(path,f)):
                if f.startswith('.'):
                    continue
                if f == '__pycache__':
                    continue
                result.append({'name':f,'type':'dir'})
            else:
                if f.endswith('.grapycal'):
                    result.append({'name':f,'path':f,'type':'workspace'})

        from grapycal import app
        result += [{'name':'Welcome.grapycal','path':os.path.join(os.path.dirname(os.path.abspath(app.__file__)),"Welcome.grapycal"),'is_dir':False}]

        return result
    
    def get_workspace_metadata(self,path):
        if path in self.metadata_cache:
            return self.metadata_cache[path]
        version, metadata, _ = read_workspace(path,metadata_only=True)
        self.metadata_cache[path] = metadata
        return metadata