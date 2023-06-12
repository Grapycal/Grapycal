import importlib

class Extension:
    def __init__(self,name:str) -> None:
        self.module = importlib.import_module(name)