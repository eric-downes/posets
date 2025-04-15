"""
Base implementations of lattice types.
"""
from typing import Dict, Set, List, Any, Optional, Iterator, Tuple, TypeVar, Callable, Union
from posets.core.finite_poset import FinitePoset
from posets.core.elements import LatticeElement, ElementFactory

T = TypeVar('T')
LE = TypeVar('LE', bound=LatticeElement)

class FiniteLattice(FinitePoset):
    """Implementation of a finite lattice."""
    
    def __init__(self, elements: List, relation: Optional[List[Tuple]] = None):
        """
        Initialize a finite lattice.
        
        Args:
            elements: The elements of the lattice
            relation: List of pairs (x, y) such that x ≤ y
                     If None, the discrete lattice (antichain with single element) is created
        """
        super().__init__(elements, relation)
        
        # Cache for meet and join operations
        self._meet_cache: Dict[Tuple[Any, Any], Any] = {}
        self._join_cache: Dict[Tuple[Any, Any], Any] = {}
        
        # Element factory for creating wrapped lattice elements
        self._element_factory = ElementFactory(self)
        
        # Verify lattice properties
        self._verify_lattice()
    
    def _verify_lattice(self) -> None:
        """Verify that this poset is indeed a lattice."""
        for x in self._elements:
            for y in self._elements:
                # Ensure meet exists
                meet_result = self.meet(x, y)
                if meet_result is None:
                    raise ValueError(f"Not a lattice: meet does not exist for {x} and {y}")
                
                # Ensure join exists
                join_result = self.join(x, y)
                if join_result is None:
                    raise ValueError(f"Not a lattice: join does not exist for {x} and {y}")
    
    def meet(self, x: Any, y: Any) -> Optional[Any]:
        """
        Compute the meet (greatest lower bound) of two elements.
        
        Args:
            x: First element
            y: Second element
            
        Returns:
            The greatest lower bound of x and y, or None if it doesn't exist
        """
        # Unwrap LatticeElement instances if needed
        if isinstance(x, LatticeElement):
            x = x.value
        if isinstance(y, LatticeElement):
            y = y.value
            
        if x not in self._element_set or y not in self._element_set:
            raise ValueError(f"Elements {x} and {y} must belong to the lattice")
        
        # Check cache
        cache_key = (x, y)
        if cache_key in self._meet_cache:
            return self._meet_cache[cache_key]
        
        # Compute the meet
        lower_bounds = [
            z for z in self._elements
            if self.__le__(z, x) and self.__le__(z, y)
        ]
        
        if not lower_bounds:
            self._meet_cache[cache_key] = None
            return None
        
        # Find the greatest lower bound
        meet_element = lower_bounds[0]
        for z in lower_bounds[1:]:
            if self.__le__(meet_element, z):
                meet_element = z
        
        self._meet_cache[cache_key] = meet_element
        return meet_element
    
    def join(self, x: Any, y: Any) -> Optional[Any]:
        """
        Compute the join (least upper bound) of two elements.
        
        Args:
            x: First element
            y: Second element
            
        Returns:
            The least upper bound of x and y, or None if it doesn't exist
        """
        # Unwrap LatticeElement instances if needed
        if isinstance(x, LatticeElement):
            x = x.value
        if isinstance(y, LatticeElement):
            y = y.value
            
        if x not in self._element_set or y not in self._element_set:
            raise ValueError(f"Elements {x} and {y} must belong to the lattice")
        
        # Check cache
        cache_key = (x, y)
        if cache_key in self._join_cache:
            return self._join_cache[cache_key]
        
        # Compute the join
        upper_bounds = [
            z for z in self._elements
            if self.__le__(x, z) and self.__le__(y, z)
        ]
        
        if not upper_bounds:
            self._join_cache[cache_key] = None
            return None
        
        # Find the least upper bound
        join_element = upper_bounds[0]
        for z in upper_bounds[1:]:
            if self.__le__(z, join_element):
                join_element = z
        
        self._join_cache[cache_key] = join_element
        return join_element
    
    def infimum(self, elements: Iterator[Any]) -> Optional[Any]:
        """
        Compute the infimum (greatest lower bound) of a set of elements.
        
        Args:
            elements: Iterator of elements
            
        Returns:
            The greatest lower bound of all elements, or None if it doesn't exist
        """
        element_list = list(elements)
        if not element_list:
            return None
        
        # Unwrap LatticeElement instances if needed
        element_list = [e.value if isinstance(e, LatticeElement) else e for e in element_list]
        
        result = element_list[0]
        for element in element_list[1:]:
            result = self.meet(result, element)
            if result is None:
                return None
        
        return result
    
    def supremum(self, elements: Iterator[Any]) -> Optional[Any]:
        """
        Compute the supremum (least upper bound) of a set of elements.
        
        Args:
            elements: Iterator of elements
            
        Returns:
            The least upper bound of all elements, or None if it doesn't exist
        """
        element_list = list(elements)
        if not element_list:
            return None
        
        # Unwrap LatticeElement instances if needed
        element_list = [e.value if isinstance(e, LatticeElement) else e for e in element_list]
        
        result = element_list[0]
        for element in element_list[1:]:
            result = self.join(result, element)
            if result is None:
                return None
        
        return result
    
    @property
    def top(self) -> Any:
        """
        Return the top element of the lattice.
        
        Returns:
            The top element (greatest element)
        
        Raises:
            ValueError: If the lattice has no unique top element
        """
        maximal = list(self.maximal_elements())
        if len(maximal) != 1:
            raise ValueError("Lattice has no unique top element")
        return maximal[0]
    
    @property
    def bottom(self) -> Any:
        """
        Return the bottom element of the lattice.
        
        Returns:
            The bottom element (least element)
        
        Raises:
            ValueError: If the lattice has no unique bottom element
        """
        minimal = list(self.minimal_elements())
        if len(minimal) != 1:
            raise ValueError("Lattice has no unique bottom element")
        return minimal[0]
    
    def element(self, value: T, hash_function: Optional[Callable[[T], int]] = None) -> LatticeElement[T, 'FiniteLattice']:
        """
        Create a wrapped lattice element.
        
        Args:
            value: The value to wrap
            hash_function: Optional custom hash function for the value
            
        Returns:
            A LatticeElement instance
            
        Raises:
            ValueError: If the value is not in the lattice
        """
        if value not in self._element_set:
            raise ValueError(f"Value {value} is not in the lattice")
        
        # If a custom hash function is provided, use it for this element
        if hash_function is not None:
            return LatticeElement(value, self, hash_function)
        
        # Otherwise use the factory's default
        return self._element_factory(value)
    
    def is_sublattice_of(self, other: 'FiniteLattice') -> bool:
        """
        Check if this lattice is a sublattice of another lattice.
        
        A lattice L is a sublattice of a lattice M if:
        1. L's elements are a subset of M's elements
        2. L's meet and join operations are the restrictions of M's 
           operations to the elements of L
        
        Args:
            other: Another lattice to check against
            
        Returns:
            True if this lattice is a sublattice of the other lattice, False otherwise
            
        Raises:
            NotImplementedError: If the sublattice relation cannot be determined
        """
        # Check if all elements of this lattice are in the other lattice
        if not all(x in other._element_set for x in self._elements):
            return False
        
        # Check that meet and join operations are preserved
        for x in self._elements:
            for y in self._elements:
                if self.meet(x, y) != other.meet(x, y):
                    return False
                if self.join(x, y) != other.join(x, y):
                    return False
        
        return True
    
    def dual(self) -> 'FiniteLattice':
        """
        Create the dual lattice by reversing the order relation.
        
        In the dual lattice:
        - x ≤ y if and only if y ≤ x in the original lattice
        - meet and join operations are swapped
        
        Returns:
            The dual lattice
        """
        # Create a new lattice with the reversed relation
        dual_relation = [(y, x) for x, y in self._get_relation()]
        dual = FiniteLattice(self._elements.copy(), dual_relation)
        return dual
    
    def _get_relation(self) -> List[Tuple[Any, Any]]:
        """Get the full binary relation of the lattice."""
        relation = []
        for x in self._elements:
            for y in self._elements:
                if self.__le__(x, y):
                    relation.append((x, y))
        return relation
    
    @classmethod
    def from_cover_relations(cls, elements: List, cover_relations: List[Tuple]) -> 'FiniteLattice':
        """
        Create a lattice directly from cover relations.
        
        Args:
            elements: The elements of the lattice
            cover_relations: List of pairs (x, y) such that y covers x
            
        Returns:
            A new FiniteLattice instance
        """
        # Create the poset from cover relations
        poset = super().from_cover_relations(elements, cover_relations)
        
        # Convert to a lattice relation
        relation = []
        for x in elements:
            for y in elements:
                if poset.__le__(x, y):
                    relation.append((x, y))
        
        # Create the lattice
        return cls(elements, relation)
    
    def set_hash_function(self, hash_function: Callable[[Any], int]) -> None:
        """
        Set a custom hash function for elements created by this lattice.
        
        This affects future elements created with the element() method.
        
        Args:
            hash_function: The hash function to use
        """
        self._element_factory = ElementFactory(self, hash_function)


class BoundedLattice(FiniteLattice):
    """
    Implementation of a bounded lattice (a lattice with top and bottom elements).
    
    A bounded lattice is guaranteed to have a unique top and bottom element.
    """
    
    def __init__(self, elements: List, relation: Optional[List[Tuple]] = None):
        """
        Initialize a bounded lattice.
        
        Args:
            elements: The elements of the lattice
            relation: List of pairs (x, y) such that x ≤ y
                     If None, the trivial bounded lattice is created
        """
        super().__init__(elements, relation)
        
        # Verify bounded lattice properties
        self._verify_bounded()
    
    def _verify_bounded(self) -> None:
        """Verify that this lattice has top and bottom elements."""
        try:
            _ = self.top
            _ = self.bottom
        except ValueError as e:
            raise ValueError("Not a bounded lattice: " + str(e))
    
    def complement(self, x: Any) -> Optional[Any]:
        """
        Find the complement of an element if it exists.
        
        In a bounded lattice, y is a complement of x if:
        - x ∧ y = 0 (bottom)
        - x ∨ y = 1 (top)
        
        Args:
            x: The element to find a complement for
            
        Returns:
            The complement of x, or None if it doesn't exist
        """
        # Unwrap LatticeElement if needed
        if isinstance(x, LatticeElement):
            x = x.value
            
        if x not in self._element_set:
            raise ValueError(f"Element {x} must belong to the lattice")
        
        # Find the complement
        for y in self._elements:
            if (self.meet(x, y) == self.bottom and 
                self.join(x, y) == self.top):
                return y
        
        return None
    
    def is_complemented(self) -> bool:
        """
        Check if this is a complemented lattice.
        
        A bounded lattice is complemented if every element has a complement.
        
        Returns:
            True if complemented, False otherwise
        """
        return all(self.complement(x) is not None for x in self._elements)