"""
Lattice element types that provide operator overloading and efficient operations.
"""
from __future__ import annotations
from typing import Any, Optional, TypeVar, Generic, Union, Callable, Dict, Tuple, Set, Protocol, Type
import functools

# Type variables
T = TypeVar('T')  # The underlying data type
L = TypeVar('L')  # The lattice type

class LatticeProxyProtocol(Protocol):
    """Protocol defining the required methods a lattice must implement for element proxying."""
    
    def __lt__(self, x: Any, y: Any) -> bool: ...
    def __le__(self, x: Any, y: Any) -> bool: ...
    def __gt__(self, x: Any, y: Any) -> bool: ...
    def __ge__(self, x: Any, y: Any) -> bool: ...
    def meet(self, x: Any, y: Any) -> Any: ...
    def join(self, x: Any, y: Any) -> Any: ...
    def is_comparable(self, x: Any, y: Any) -> bool: ...
    def is_sublattice_of(self, other: Any) -> bool: ...

class LatticeElement(Generic[T, L]):
    """
    A wrapper for lattice elements that provides operator overloading.
    
    This class allows natural syntax for lattice operations by delegating
    all operations to the parent lattice:
    - e1 <= e2   (checks if e1 ≤ e2 in the lattice ordering)
    - e1 < e2    (checks if e1 < e2 in the lattice ordering)
    - e1 & e2    (computes the meet, e1 ∧ e2)
    - e1 | e2    (computes the join, e1 ∨ e2)
    
    It maintains a reference to its parent lattice for operations, ensuring
    that the element always inherits the semantics of its parent lattice.
    """
    __slots__ = ('_value', '_lattice', '_cache', '_hash')
    
    def __init__(self, value: T, lattice: L, hash_function: Optional[Callable[[T], int]] = None):
        """
        Initialize a lattice element.
        
        Args:
            value: The wrapped value
            lattice: The parent lattice this element belongs to
            hash_function: Optional custom hash function for the value
        """
        self._value = value
        self._lattice = lattice
        self._cache: Dict[Tuple[str, Any], Any] = {}
        
        # Pre-compute hash if a custom hash function is provided
        if hash_function is not None:
            self._hash = hash_function(value)
        else:
            self._hash = None
    
    @property
    def value(self) -> T:
        """Get the underlying value."""
        return self._value
    
    @property
    def lattice(self) -> L:
        """Get the parent lattice."""
        return self._lattice
    
    def __eq__(self, other: Any) -> bool:
        """
        Test equality of lattice elements.
        
        Two lattice elements are equal if:
        1. They have the same value, and
        2. They belong to the same lattice OR one lattice is a sublattice of the other
        
        Raw values are compared directly with the wrapped value.
        """
        if isinstance(other, LatticeElement):
            # Check for compatibility of lattices
            if self._lattice is other._lattice:
                return self._value == other._value
            
            # Check if one lattice is a sublattice of the other
            try:
                if hasattr(self._lattice, 'is_sublattice_of') and self._lattice.is_sublattice_of(other._lattice):
                    return self._value == other._value
                if hasattr(other._lattice, 'is_sublattice_of') and other._lattice.is_sublattice_of(self._lattice):
                    return self._value == other._value
            except (AttributeError, NotImplementedError):
                pass
            
            # Not compatible - not equal
            return False
        
        # Direct comparison with raw value
        return self._value == other
    
    def __hash__(self) -> int:
        """
        Make lattice elements hashable.
        
        Uses a custom hash function if provided, otherwise defaults to
        hashing the tuple (value, lattice_id).
        """
        if self._hash is not None:
            return self._hash
        return hash((self._value, id(self._lattice)))
    
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
            - other_value: The extracted value from other if it's a LatticeElement
            
        Raises:
            ValueError: If strict is True and elements are from incompatible lattices
        """
        if isinstance(other, LatticeElement):
            # Same lattice - always compatible
            if self._lattice is other._lattice:
                return True, other._value
            
            # Check if one lattice is a sublattice of the other
            try:
                if hasattr(self._lattice, 'is_sublattice_of') and self._lattice.is_sublattice_of(other._lattice):
                    return True, other._value
                if hasattr(other._lattice, 'is_sublattice_of') and other._lattice.is_sublattice_of(self._lattice):
                    return True, other._value
            except (AttributeError, NotImplementedError):
                pass
            
            # Incompatible lattices
            if strict:
                raise ValueError("Cannot compare elements from incompatible lattices")
            return False, None
        
        # Raw value - always compatible
        return True, other
    
    def __lt__(self, other: Any) -> bool:
        """
        Test if self < other in the lattice ordering.
        
        This operation delegates to the parent lattice's __lt__ method.
        
        Args:
            other: Another lattice element or raw value
            
        Returns:
            True if self < other in the lattice ordering, False otherwise
            
        Raises:
            ValueError: If elements are from incompatible lattices and the 
                       lattice enforces strict compatibility checking
        """
        compatible, other_value = self._check_compatibility(other)
        if not compatible:
            return False
        
        cache_key = ('lt', other_value)
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        result = self._lattice.__lt__(self._value, other_value)
        self._cache[cache_key] = result
        return result
    
    def __le__(self, other: Any) -> bool:
        """
        Test if self ≤ other in the lattice ordering.
        
        This operation delegates to the parent lattice's __le__ method.
        
        Args:
            other: Another lattice element or raw value
            
        Returns:
            True if self ≤ other in the lattice ordering, False otherwise
            
        Raises:
            ValueError: If elements are from incompatible lattices and the 
                       lattice enforces strict compatibility checking
        """
        compatible, other_value = self._check_compatibility(other)
        if not compatible:
            return False
        
        cache_key = ('le', other_value)
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        result = self._lattice.__le__(self._value, other_value)
        self._cache[cache_key] = result
        return result
    
    def __gt__(self, other: Any) -> bool:
        """
        Test if self > other in the lattice ordering.
        
        This operation delegates to the parent lattice's __gt__ method.
        
        Args:
            other: Another lattice element or raw value
            
        Returns:
            True if self > other in the lattice ordering, False otherwise
            
        Raises:
            ValueError: If elements are from incompatible lattices and the 
                       lattice enforces strict compatibility checking
        """
        compatible, other_value = self._check_compatibility(other)
        if not compatible:
            return False
        
        cache_key = ('gt', other_value)
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        result = self._lattice.__gt__(self._value, other_value)
        self._cache[cache_key] = result
        return result
    
    def __ge__(self, other: Any) -> bool:
        """
        Test if self ≥ other in the lattice ordering.
        
        This operation delegates to the parent lattice's __ge__ method.
        
        Args:
            other: Another lattice element or raw value
            
        Returns:
            True if self ≥ other in the lattice ordering, False otherwise
            
        Raises:
            ValueError: If elements are from incompatible lattices and the 
                       lattice enforces strict compatibility checking
        """
        compatible, other_value = self._check_compatibility(other)
        if not compatible:
            return False
        
        cache_key = ('ge', other_value)
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        result = self._lattice.__ge__(self._value, other_value)
        self._cache[cache_key] = result
        return result
    
    def __and__(self, other: Any) -> Optional[LatticeElement[T, L]]:
        """
        Compute the meet (greatest lower bound) of self and other.
        
        This operation delegates to the parent lattice's meet method.
        
        Args:
            other: Another lattice element or raw value
            
        Returns:
            The meet of self and other as a LatticeElement, or None if 
            elements are incompatible
            
        Raises:
            ValueError: If elements are from incompatible lattices and the 
                       lattice enforces strict compatibility checking
        """
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
        """
        Compute the join (least upper bound) of self and other.
        
        This operation delegates to the parent lattice's join method.
        
        Args:
            other: Another lattice element or raw value
            
        Returns:
            The join of self and other as a LatticeElement, or None if 
            elements are incompatible
            
        Raises:
            ValueError: If elements are from incompatible lattices and the 
                       lattice enforces strict compatibility checking
        """
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
    
    def is_comparable(self, other: Any) -> bool:
        """
        Check if this element is comparable with another element.
        
        Two elements are comparable if one is less than or equal to the other.
        
        Args:
            other: Another lattice element or raw value
            
        Returns:
            True if the elements are comparable, False otherwise
        """
        compatible, other_value = self._check_compatibility(other)
        if not compatible:
            return False
        
        cache_key = ('comparable', other_value)
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        result = self._lattice.is_comparable(self._value, other_value)
        self._cache[cache_key] = result
        return result
    
    def clear_cache(self) -> None:
        """Clear the cache of operation results."""
        self._cache.clear()
    
    def __repr__(self) -> str:
        """String representation of the lattice element."""
        return f"LatticeElement({repr(self._value)})"
    
    def __str__(self) -> str:
        """String representation of the lattice element."""
        return str(self._value)


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