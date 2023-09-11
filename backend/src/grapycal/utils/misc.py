from typing import Any, Callable, List, TypeVar

T = TypeVar('T')
def as_type(x, t: type[T]) -> T:
    assert isinstance(x, t)
    return x


class Action:
    '''
    A hub for callbacks
    '''
    def __init__(self):
        self.callbacks:List[Callable] = []

    def __add__(self,callback:Callable):
        '''
        Temporary backward compatibility. To be removed.
        '''
        self.callbacks.append(callback)
        return self
    
    def __sub__(self,callback:Callable):
        '''
        Temporary backward compatibility. To be removed.
        '''
        self.callbacks.remove(callback)
        return self
    
    def invoke(self, *args: Any, **kwargs: Any) -> Any:
        '''Call each callback in the action with the given arguments.'''
        returns = []
        for callback in self.callbacks:
            returns.append(callback(*args,**kwargs))
        return returns