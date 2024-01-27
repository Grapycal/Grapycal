from objectsync import DictTopic, SObject

class Settings(SObject):
    frontend_type = 'Settings'

    def build(self,old=None):
        self.entries = self.add_attribute('entries',DictTopic,{})

    def init(self):
        pass
        # self.entries.add('test',{"name": "a/0_64772/dtype", "display_name": "Appearance/dtype", "editor_args": {"options": ["float32", "float64", "int32", "int64", "bool"], "type": "options"}})