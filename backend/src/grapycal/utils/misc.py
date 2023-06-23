from typing import TypeVar

T = TypeVar('T')
def as_type(x, t: type[T]) -> T:
    assert isinstance(x, t)
    return x