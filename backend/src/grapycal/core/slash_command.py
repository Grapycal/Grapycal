from dataclasses import dataclass
from typing import Callable, Dict

from objectsync import DictTopic


# @dataclass
# class SlashCommand:
#     name: str
#     callback: Callable
#     source: str
#     key: str
#     display_name: str

class Command:
    def __init__(self, name: str, callback: Callable, source: str, key: str|None=None, display_name: str|None=None,prefix='/'):
        self.name = name
        self.callback = callback
        self.source = source
        self.key = key or name
        self.display_name = display_name or name

        self.key = prefix + self.key
        self.display_name = prefix + self.display_name

    def __repr__(self):
        return f"<SlashCommand {self.name}>"
    
    def to_dict(self):
        return {
            "name": self.name,
            "source": self.source,
            "key": self.key,
            "display_name": self.display_name
        }



class SlashCommandManager:
    def __init__(self, topic:DictTopic):
        self._commands: Dict[str, Command] = {}
        self._topic = topic
    
    def register(self, name: str, callback: Callable, source: str=""):
        command = Command(name, callback, source)
        if command.name in self._commands:
            raise ValueError(f"Command {command.name} already exists")
        self._commands[command.name] = command
        self._topic.add(name, command.to_dict())

    def unregister(self, name: str):
        if name not in self._commands:
            raise ValueError(f"Command {name} does not exist")
        del self._commands[name]
        self._topic.pop(name)

    def call(self, name: str, *args, **kwargs):
        if name not in self._commands:
            raise ValueError(f"Command {name} does not exist")
        self._commands[name].callback(*args, **kwargs)
    
    def unregister_source(self, source: str):
        for name, command in self._commands.copy().items():
            if command.source == source:
                del self._commands[name]
                self._topic.pop(name)