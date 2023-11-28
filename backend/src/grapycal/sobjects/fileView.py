import os
from objectsync import SObject


class FileView(SObject):
    frontend_type = 'FileView'
    def init(self):
        self.register_service('ls',self.ls)

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
                result.append({'name':f,'is_dir':True})
            else:
                result.append({'name':f,'is_dir':False})

        return result