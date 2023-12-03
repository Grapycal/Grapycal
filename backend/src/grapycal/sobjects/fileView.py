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
                if f.startswith('.'):
                    continue
                if f == '__pycache__':
                    continue
                result.append({'name':f,'is_dir':True})
            else:
                if f.endswith('.grapycal'):
                    result.append({'name':f,'path':f,'is_dir':False})

        from grapycal import app
        result += [{'name':'Welcome.grapycal','path':os.path.join(os.path.dirname(os.path.abspath(app.__file__)),"Welcome.grapycal"),'is_dir':False}]

        return result