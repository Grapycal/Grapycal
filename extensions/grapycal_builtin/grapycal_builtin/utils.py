from typing import Iterable
from typing import Dict
from typing import List
from typing import TypeVar
from typing import Generic

T = TypeVar('T')
class ListDict(Generic[T]):
    def __init__(self):
        self.d:Dict[str,List[T]] = {}

    def append(self, key:str, value:T):
        if key not in self.d:
            self.d[key] = []
        self.d[key].append(value)

    def remove(self, key:str, value:T):
        self.d[key].remove(value)
        if len(self.d[key]) == 0:
            self.d.pop(key)

    def has(self, key:str):
        return key in self.d
    
    def get(self, key:str):
        if key not in self.d:
            return []
        return self.d[key]


def find_next_valid_name(name:str, invalids:Iterable[str]):
    # base -> base(1) -> base(2) -> ...
    
    if name == '':
        return name
    if name not in invalids:
        return name
    
    # separate base and number
    base = name
    number = 1
    if '(' in name and name[-1] == ')':
        base = name[:name.rfind('(')]
        number = name[name.rfind('(')+1:-1]
        try:
            number = int(number)
        except:
            base = name
            number = 1

    while True:
        new_name = f'{base}({number})'
        if new_name not in invalids:
            return new_name
        number += 1
