from __future__ import annotations
from typing import Callable, Generic, TypeVar

X,Y,Z = map(TypeVar, 'XYZ')
BoolOp = Callable[[X,X], bool]
class Infix(Generic[X,Y]):
    def __init__(self, op:BoolOp[X], lhs:BoolOp[Y] = None):
        self.op = op
        self.lhs = lhs
    def __call__(self, *args, **kwargs):
        return self.op(*args, **kwargs)
    def __ror__(self, lhs:BoolOp[Y]):
        return __class__(self.op, lhs)
    def __or__(self, rhs:BoolOp[Y]):
        return self(self.lhs, rhs)
     
def comparable(a:X, b:X, strict:bool = False) -> bool|None:
    try: return (a <= b) | (a > b)
    except TypeError as e:
        if strict: raise e
        return None
    
comp = Infix(comparable)

class Elem(Generic[Z]):
    def __init__(self, val:Z):
        self.val = val
    def __lt__(self, other:Elem[Z]) -> bool:
        return self.val < other.val
    def __gt__(self, other:Elem[Z]) -> bool:
        return self.val > other.val
    def __eq__(self, other:Elem[Z]) -> bool:
        return self.val == other.val
    def __ge__(self, other:Elem[Z]) -> bool:
        return (self > other) | (self == other)
    def __le__(self, other:Elem[Z]) -> bool:
        return (self < other) | (self == other)
    

assert 4 |comp| 5
assert ('s' |comp| 19) is None
assert Elem(22) |comp| Elem(6)
assert (Elem(33) |comp| Elem('s')) is None
