"""Lattice element types that provide operator overloading and efficient operations.

current push:

- every lattice we actually instantiate will be a MaterialLattice, even if infinite
- a MaterialLattice is an element of an implicit powerset lattice that contains it
- possibly as its only member as default
- this allows us to use the same lattice operations to determin sublattices etc.
- When we make new sublattices, we must update the parent lattice.
- then we have FiniteLattice(MaterialLattice), InfiniteLattice(MaterialLattice)

eventually I'd like to similarly make a
Poset(Protocol)
Monoid(Protocol)
SemiLattice(Monoid, Poset, Idempotent, Commutative)
Lattice(SemiLattice, SelfDual)

and make Material a more general transformation that embeds an X in a powerset/universe

"""
from __future__ import annotations
from typing import (
    Any, TypeVar, Generic, Union, Callable, Dict, Tuple, Set,
    Protocol, Type, Hashable, cast)
import functools
import operators as ops

#from infix import comp # use matmul instead

# Type variables
H = TypeVar('H', bytes, str, int)
T = TypeVar('T', bound=Hashable, covariant=True) # wrapped type
CoT = TypeVar('CoT', bound=Hashable, contravariant=True)
L = TypeVar('L')  # The lattice type
class HashFcn(Generic[CoT, H]): # here to create (T <=) & Hashable w/o type intersections
    @abstractmethod
    def __call__(self, obj: CoT) -> H: ...
hashTint = cast(HashFcn[T,int], hash)

# classes

class GenObject(Protocol):
    

class AbstractPoset(Protocol):
    def le(self, x: KlElem[L,T], y: KlElem[L,T]) -> bool:
        return self.lt(x, y) | self.eq(x, y)
    def ge(self, x: KlElem[L,T], y: KlElem[L,T]) -> bool:
        return self.gt(x, y) | self.eq(x, y)        
    def comp(self, x: KlElem[L,T], y: KlElem[L,T]) -> bool:
        return self.lt(x, y) | self.ge(x, y) 
    @abstractmethod
    def eq(self, x: KlElem[L,T], y: KlElem[L,T]) -> bool:
    @abstractmethod
    def lt(self, x: KlElem[L,T], y: KlElem[L,T]) -> bool: ...
    @abstractmethod
    def gt(self, x: KlElem[L,T], y: KlElem[L,T]) -> bool: ...    

class AbstractLattice(Protocol, AbstractPoset):
    @abstractmethod
    def meet(self, x: KlElem[L,T], y: KlElem[L,T]) -> KlElem: ...
    @abstractmethod
    def join(self, x: KlElem[L,T], y: KlElem[L,T]) -> KlElem: ...

class OneElementPoset(Protocol, AbstractLattice):
    def __init__(self, member:Any):
        self.members = frozenset(StructuralPosetElement(self, member))
    def eq(self, x: Any, y: Any) -> bool:
        return x is y and x in self.members
    def lt(self, x: Any, y: Any) -> bool:
        return False
    def gt(self, x: Any, y: Any) -> bool:
        return False
    
class OneElementLattice(Protocol, OneElementPoset, AbstractLattice):
    

    
class ASbstractPoset(Protocol)

class StructuralLatticeElement(StructuralPosetElement, AbstractLattice)

class MaterialPoset(AbstractPoset, StructuralLatticeElement):
    def __init__(self,
                 members:dict = None,
                 containment_lattice:AbstractLattice = None):
        self._pwrlat = containment_lattice or OneElementLattice(self)
        self._members = members or {}

class StructuralPoset(AbstractPoset, MaterialPosetElement):
    def __init__(self, members:dict = None):
        self._members = members or {}
        self._poset = MaterialPoset(members = {self}

class AbstractPosetElement(Protocol):
    __slots__ = ('_poset')
    """Abstract Element defines necessary logic"""
    @property
    def poset(self) -> AbstractPoset:
        return self._poset
    def __le__(self, other: AbstractPosetElement) -> bool:
        return (self < other) | (self == other)
    def __ge__(self, other: AbstractPosetElement) -> bool:
        return (self > other) | (self == other)
    def __matmul__(self, other: AbstractPosetElement) -> bool: # comparable
        return (self <= other) | (self > other)
    def __rmatmul__(self, other: AbstractPosetElement) -> bool: # comparable
        return other.__matmul__(self)
    @abstractmethod
    def __eq__(self, other: AbstractPosetElement) -> bool: ...
    @abstractmethod
    def __lt__(self, other: AbstractPosetElement) -> bool: ...
    @abstractmethod
    def __gt__(self, other: AbstractPosetElement) -> bool: ...

class StructuralPosetElement(AbstractPosetElement):
    def __eq__(self, other: AbstElem[L,T]) -> bool:    
        return self.poset().eq(self, other)
    def __lt__(self, other: AbstElem[L,T]) -> bool:
        return self.poset().lt(self, other)
    def __gt__(self, other: AbstElem[L,T]) -> bool:
        return self.poset().gt(self, other)
    def materialize(self) -> MaterialPosetElement:
        raise NotImplementedError()

class MaterialPosetElement(AbstractPosetElement):
    def __init__(self,
                 value:T,
                 poset:L,
                 hashfcn:HashFcn[T,int] = hashTint):
        self._value = value
        self._hashfcn = hashfcn
        self._poset = poset
    @property
    def value(self) -> T: return self._value
    @property
    def __hash__(self) -> S: return self._hashfcn(self)    
    def __eq__(self, other: AbstElem[L,T]) -> bool:    
        return self._op_(ops.eq, other)
    def __lt__(self, other: AbstElem[L,T]) -> bool:
        return self._op_(ops.lt, other)
    def __gt__(self, other: AbstElem[L,T]) -> bool:
        return self._op_(ops.lt, other)
    def _op_(self, op:Callable[[T,T], bool], other:MaterialPosetElement) -> bool:
        try:
            if (p := self.poset()) @ other.poset():
               return p.op(self.value(), op, other.value())
            raise TypeError('Enclosing Posets not comparable')
        except (AttributeError, NotImplementedError, TypeError) as e:
            if strict: raise e
            return None


        

class AbstPoset(MaterialElement): # Abstract Poset
    def __init__(self, containing_lattice:Lattice = None):
        self._containing_lattice = containing_lattice
    def my_containing_lattice(self) -> Lattice:
        if self._containing_lattice is None:
            pwr = EmptyLattice()
            pwr.adjoin_element(self, top = True)
            self._containing_lattice = pwr
        return self._containing_lattice
    """Protocol defining the default and required methods a poset must implement for element proxying."""

    def materialize(self) -> MaterialPoset:
        """Materialize this abstract poset into a concrete one."""
        if self.is_abstract():            
            # Lazy evaluation - construct the material poset
            # needs to update all other posets having self as a parent
            # new = MaterialPoset.from_element(self)
            # elements = [...] # Generate elements from base poset
            # self._materialized = MaterialPoset(elements)
            raise NotImplementedError('no material today')

class MaterialPoset(AbstPoset):

            
            
            self._my_pwrlat = AbstLattice(members = {
            
            
        
    def materialize(self) -> MaterialPoset: return self        
        

        
class PosetElement(AbstElem):
    """
    A wrapper for poset elements delegating operators to the parent poset:
      - e1 <= e2   (checks if e1 ≤ e2 in the lattice ordering)
      - e1 < e2    (checks if e1 < e2 in the lattice ordering)    
    It maintains a reference to its parent lattice for operations, ensuring
    that the element always inherits the semantics of its parent lattice.
    """
    __slots__ = ('_value', '_poset', '_cache', '_hash')    
    def __init__(self,
                 value: T, # The wrapped value
                 poset: AbstPoset, # The parent poset this element belongs to
                 hash_function: HashFcn[T,int] = hashTint):
        self._value = value
        self._poset = poset
        self._cache: Dict[Tuple[str, Any], Any] = {}
        self._hashfcn = hash_function

    def __eq__(self, other: AbstElem[L,T]) -> bool:
        return self._op_(self.poset().eq, other)
    def __lt__(self, other: AbstElem[L,T]) -> bool:
        return self._op_(self.poset().lt, other)        
    def __gt__(self, other: AbstElem[L,T]) -> bool:
        return self._op_(self.poset().gt, other)
            
            
    
    def __eq__(self, other: Any) -> bool:
        return self._op_(ops.eq

            # Check if one poset is a subposet of the other
            try:
                if self._poset <= other._poset or self._poset >= other._poset:
                    return self._value == other._value
            except 
                if strict: raise e
            return False
        # Direct comparison with raw value e.g. treat these as elements of material sets
        return self._value == other

    @property
    def __hash__(self) -> int:
        if self._hash is not None:
            return self._hash
        return hash((self._value, id(self._poset)))
    
    def _check_compatibility(self, other: Any, strict: bool = False) -> Tuple[bool, Any]:
        """
        Check if this element can be compared with another element or value.
        
        Args:
            other: The other element or value to compare with
            strict: If True, raise an exception for incompatible elements;
                   If False, return False for incompatible elements
                   
        Returns:
            Tuple of (is_compatible, other_value)
            - is_compatible: True if the elements can be compared
            - other_value: The extracted value from other if it's a PosetElement
            
        Raises:
            ValueError: If strict is True and elements are from incompatible posets
        """
        if isinstance(other, PosetElement):
            # Same poset - always compatible
            if self._poset is other._poset:
                return True, other._value
            
            # Check if one poset is a subposet of the other
            try:
                if hasattr(self._poset, 'is_subposet_of') and self._poset.is_subposet_of(other._poset):
                    return True, other._value
                if hasattr(other._poset, 'is_subposet_of') and other._poset.is_subposet_of(self._poset):
                    return True, other._value
            except (AttributeError, NotImplementedError):
                pass
            
            # Incompatible posets
            if strict:
                raise TypeError("Cannot compare elements from incompatible posets")
            return False, None
        
        # Raw value - always compatible
        return True, other
    
    def __lt__(self, other: Any) -> bool:
        """
        Test if self < other in the poset ordering.
        
        This operation delegates to the parent poset's __lt__ method.
        
        Args:
            other: Another poset element or raw value
            
        Returns:
            True if self < other in the poset ordering, False otherwise
            
        Raises:
            ValueError: If elements are from incompatible posets and the 
                       poset enforces strict compatibility checking
        """
        compatible, other_value = self._check_compatibility(other)
        if not compatible:
            return False
        
        cache_key = ('lt', other_value)
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        result = self._poset.__lt__(self._value, other_value)
        self._cache[cache_key] = result
        return result
    
    def __le__(self, other: Any) -> bool:
        """
        Test if self ≤ other in the poset ordering.
        
        This operation delegates to the parent poset's __le__ method.
        
        Args:
            other: Another poset element or raw value
            
        Returns:
            True if self ≤ other in the poset ordering, False otherwise
            
        Raises:
            ValueError: If elements are from incompatible posets and the 
                       poset enforces strict compatibility checking
        """
        compatible, other_value = self._check_compatibility(other)
        if not compatible:
            return False
        
        cache_key = ('le', other_value)
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        result = self._poset.__le__(self._value, other_value)
        self._cache[cache_key] = result
        return result
    
    def __gt__(self, other: Any) -> bool:
        """
        Test if self > other in the poset ordering.
        
        This operation delegates to the parent poset's __gt__ method.
        
        Args:
            other: Another poset element or raw value
            
        Returns:
            True if self > other in the poset ordering, False otherwise
            
        Raises:
            ValueError: If elements are from incompatible posets and the 
                       poset enforces strict compatibility checking
        """
        compatible, other_value = self._check_compatibility(other)
        if not compatible:
            return False
        
        cache_key = ('gt', other_value)
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        result = self._poset.__gt__(self._value, other_value)
        self._cache[cache_key] = result
        return result
    
    def __ge__(self, other: Any) -> bool:
        """
        Test if self ≥ other in the poset ordering.
        
        This operation delegates to the parent poset's __ge__ method.
        
        Args:
            other: Another poset element or raw value
            
        Returns:
            True if self ≥ other in the poset ordering, False otherwise
            
        Raises:
            ValueError: If elements are from incompatible posets and the 
                       poset enforces strict compatibility checking
        """
        compatible, other_value = self._check_compatibility(other)
        if not compatible:
            return False
        
        cache_key = ('ge', other_value)
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        result = self._poset.__ge__(self._value, other_value)
        self._cache[cache_key] = result
        return result

    def is_comparable(self, other: Any) -> bool:
        """
        Check if this element is comparable with another element.
        
        Two elements are comparable if one is less than or equal to the other.
        
        Args:
            other: Another poset element or raw value
            
        Returns:
            True if the elements are comparable, False otherwise
        """
        compatible, other_value = self._check_compatibility(other)
        if not compatible:
            return False
        
        cache_key = ('comparable', other_value)
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        result = self._poset.is_comparable(self._value, other_value)
        self._cache[cache_key] = result
        return result
    
    def clear_cache(self) -> None:
        """Clear the cache of operation results."""
        self._cache.clear()
    
    def __repr__(self) -> str:
        """String representation of the poset element."""
        return f"PosetElement({repr(self._value)})"
    
    def __str__(self) -> str:
        """String representation of the poset element."""
        return str(self._value)

class MaterialPoset(PosetElement, AbstractPoset):
    def __init__(self,
                 underlying_set: set,
                 parent_poset: MaterialPoset = None):
        self._underset = underlying_set
        self._parent = parent or MaterialPoset(underlying_set = {self})
    def is_subposet_of(self, other: Any) -> bool:
        return self.__le__(self, other)


class AbstractLattice(AbstractPoset):
    def __and__(self, other: Any) -> LatticeElement[T, L]|None:
        """Compute the meet (greatest lower bound) of self and other."""
        compatible, other_value = self._check_compatibility(other, strict=True)
        if not compatible:
            return None
        
        cache_key = ('meet', other_value)
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        result_value = self._lattice.meet(self._value, other_value)
        if result_value is None:
            return None
            
        result = self.__class__(result_value, self._lattice)
        self._cache[cache_key] = result
        return result
    
    def __or__(self, other: Any) -> Optional[LatticeElement[T, L]]:
        """Compute the join (least upper bound) of self and other."""
        compatible, other_value = self._check_compatibility(other, strict=True)
        if not compatible:
            return None
        
        cache_key = ('join', other_value)
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        result_value = self._lattice.join(self._value, other_value)
        if result_value is None:
            return None
            
        result = self.__class__(result_value, self._lattice)
        self._cache[cache_key] = result
        return result
    

    


    
class AbstractPosetElement(Protocol)
    
class PosetProxyProtocol(Protocol):


class LatticeProxyProtocol(PosetProxyProtocol):    
    def meet(self, x: Any, y: Any) -> Any: ...
    def join(self, x: Any, y: Any) -> Any: ...




    
class LatticeElement(PosetElement):
    """
    - e1 & e2    (computes the meet, e1 ∧ e2)
    - e1 | e2    (computes the join, e1 ∨ e2)
    """




class ElementFactory:
    """
    Factory class to create lattice elements for a specific lattice.
    
    This provides a convenient way to create elements that are automatically
    associated with a specific lattice instance.
    """
    def __init__(self, lattice: Any, hash_function: Optional[Callable[[Any], int]] = None):
        """
        Initialize the element factory.
        
        Args:
            lattice: The lattice to create elements for
            hash_function: Optional custom hash function for values
        """
        self._lattice = lattice
        self._hash_function = hash_function
    
    def __call__(self, value: T) -> LatticeElement[T, Any]:
        """
        Create a new lattice element.
        
        Args:
            value: The value to wrap in a lattice element
            
        Returns:
            A new LatticeElement instance for the given value
        """
        return LatticeElement(value, self._lattice, self._hash_function)
