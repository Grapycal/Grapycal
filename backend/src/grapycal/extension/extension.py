import importlib

class Extension:
    def __init__(self,name:str) -> None:
        self.module = importlib.import_module(name)
        self.name = name
        self.base_name ='_'.join( name.split('_')[:-1])
    