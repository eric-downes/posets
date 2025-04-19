"""
Tests for lattice element types and operations.
"""
import pytest
from typing import List, Set, Any, Optional

# These imports will work once we implement the actual code
from posets.core.elements import LatticeElement, ElementFactory, HashFcn
from posets.core.factories import boolean_lattice, powerset_lattice
from posets.lattice.base import FiniteLattice

# For testing with static type checkers (mypy/pyright)
def test_with_static_checker():
    class Base(Hashable): 
        def __hash__(self) -> int: return 1
    
    class Sub(Base): pass

    def f(t: T, h: HashFunction[T] = cast(HashFunction[T], hash)) -> int:
        return h(t)
    
    # These should pass type checking:
    hash_base: HashFcn[Base] = cast(HashFcn[Base], hash)
    hash_any: HashFcn[Hashable] = cast(HashFcn[Hashable], hash)
    
    # Using with proper subtyping:
    sub = Sub()
    f(sub, hash_base)  # OK: hash_base accepts Base, which is supertype of Sub
    f(sub, hash_any)   # OK: hash_any accepts Hashable, supertype of Sub
    
    # This should fail type checking:
    # hash_sub: HashFcn[Sub] = hash_base  # Error: contravariance



class TestLatticeElements:
    """Tests for the LatticeElement wrapper class."""
    
    def test_element_creation(self, diamond_poset):
        """Test creation of lattice elements and their basic properties."""
        lattice = FiniteLattice(
            diamond_poset._elements, 
            [(x, y) for x in diamond_poset._elements for y in diamond_poset._elements 
             if diamond_poset.__le__(x, y)]
        )
        
        # Create wrapped elements
        bottom = lattice.element("0")
        a = lattice.element("a")
        b = lattice.element("b")
        c = lattice.element("c")
        top = lattice.element("1")
        
        # Check element properties
        assert bottom.value == "0"
        assert a.lattice is lattice
        assert b.value == "b"
        assert top.lattice is lattice
        
        # Test equality
        assert bottom == bottom
        assert bottom != a
        assert a != b
        
        # Test equality with unwrapped values
        assert bottom == "0"
        assert a == "a"
        assert top == "1"
    
    def test_element_comparisons(self, diamond_poset):
        """Test comparison operations for lattice elements."""
        lattice = FiniteLattice(
            diamond_poset._elements, 
            [(x, y) for x in diamond_poset._elements for y in diamond_poset._elements 
             if diamond_poset.__le__(x, y)]
        )
        
        # Create wrapped elements
        bottom = lattice.element("0")
        a = lattice.element("a")
        b = lattice.element("b")
        c = lattice.element("c")
        top = lattice.element("1")
        
        # Test less than
        assert bottom < a
        assert bottom < b
        assert a < top
        assert not a < b
        assert not b < a
        
        # Test less than or equal
        assert bottom <= a
        assert a <= a  # Reflexivity
        assert a <= top
        assert not a <= b
        
        # Test greater than
        assert top > a
        assert a > bottom
        assert not a > b
        
        # Test greater than or equal
        assert top >= a
        assert a >= a  # Reflexivity
        assert a >= bottom
        assert not a >= b
        
        # Test comparisons with unwrapped values
        assert bottom < "a"
        assert "a" < top
        assert bottom <= "0"  # Reflexive with raw value
        assert not "a" <= "b"
    
    def test_meet_join_operations(self, diamond_poset):
        """Test meet and join operations for lattice elements."""
        lattice = FiniteLattice(
            diamond_poset._elements, 
            [(x, y) for x in diamond_poset._elements for y in diamond_poset._elements 
             if diamond_poset.__le__(x, y)]
        )
        
        # Create wrapped elements
        bottom = lattice.element("0")
        a = lattice.element("a")
        b = lattice.element("b")
        c = lattice.element("c")
        top = lattice.element("1")
        
        # Test meet operation (&)
        assert (a & b) == bottom
        assert (a & c) == bottom
        assert (a & a) == a  # Idempotent
        assert (a & top) == a
        assert (bottom & a) == bottom
        
        # Test join operation (|)
        assert (a | b) == top
        assert (a | c) == top
        assert (a | a) == a  # Idempotent
        assert (a | bottom) == a
        assert (top | a) == top
        
        # Test operations with unwrapped values
        assert (a & "b") == bottom
        assert (a | "b") == top
        assert ("a" & b) == bottom
        assert ("a" | b) == top
    
    def test_element_caching(self, diamond_poset):
        """Test that operations are properly cached for efficiency."""
        lattice = FiniteLattice(
            diamond_poset._elements, 
            [(x, y) for x in diamond_poset._elements for y in diamond_poset._elements 
             if diamond_poset.__le__(x, y)]
        )
        
        # Create wrapped elements
        a = lattice.element("a")
        b = lattice.element("b")
        
        # Perform operations to fill cache
        result1 = a & b
        result2 = a | b
        
        # Modify internal cache tracking to verify it's being used
        original_meet = lattice.meet
        original_join = lattice.join
        
        call_count = {'meet': 0, 'join': 0}
        
        def counting_meet(x, y):
            call_count['meet'] += 1
            return original_meet(x, y)
        
        def counting_join(x, y):
            call_count['join'] += 1
            return original_join(x, y)
        
        lattice.meet = counting_meet
        lattice.join = counting_join
        
        # Operations should use cache now
        result3 = a & b
        result4 = a | b
        
        # The lattice's meet/join methods should not have been called again
        assert call_count['meet'] == 0
        assert call_count['join'] == 0
        
        # Results should be the same
        assert result1 == result3
        assert result2 == result4
        
        # Clear cache and perform again
        a.clear_cache()
        result5 = a & b
        result6 = a | b
        
        # Now the methods should have been called
        assert call_count['meet'] == 1
        assert call_count['join'] == 1
        
        # Restore original methods
        lattice.meet = original_meet
        lattice.join = original_join
    
    def test_element_factory(self, boolean_3_lattice):
        """Test the ElementFactory for creating lattice elements."""
        factory = ElementFactory(boolean_3_lattice)
        
        # Create elements using the factory
        empty = factory(frozenset())
        s1 = factory(frozenset({0}))
        s2 = factory(frozenset({1}))
        s12 = factory(frozenset({0, 1}))
        
        # Check basic properties
        assert empty.value == frozenset()
        assert empty.lattice is boolean_3_lattice
        
        # Test operations
        assert (s1 & s2) == empty
        assert (s1 | s2) == s12
    
    def test_different_lattices_comparison(self, diamond_poset, pentagon_poset):
        """Test that comparing elements from different lattices raises an error."""
        diamond_lattice = FiniteLattice(
            diamond_poset._elements, 
            [(x, y) for x in diamond_poset._elements for y in diamond_poset._elements 
             if diamond_poset.__le__(x, y)]
        )
        
        pentagon_lattice = FiniteLattice(
            pentagon_poset._elements, 
            [(x, y) for x in pentagon_poset._elements for y in pentagon_poset._elements 
             if pentagon_poset.__le__(x, y)]
        )
        
        # Create elements from different lattices
        diamond_a = diamond_lattice.element("a")
        pentagon_a = pentagon_lattice.element("a")
        
        # Cannot compare elements from different lattices
        with pytest.raises(ValueError):
            result = diamond_a & pentagon_a
            
        # Non-strict comparison should return False
        assert not (diamond_a < pentagon_a)
        assert not (diamond_a <= pentagon_a)
        assert not (diamond_a > pentagon_a)
        assert not (diamond_a >= pentagon_a)
    
    def test_algebraic_properties_with_elements(self):
        """Test algebraic properties using lattice elements."""
        p = powerset_lattice({1, 2, 3})
        
        # Create wrapped elements
        empty = p.element(frozenset())
        s1 = p.element(frozenset({1}))
        s2 = p.element(frozenset({2}))
        s3 = p.element(frozenset({3}))
        s12 = p.element(frozenset({1, 2}))
        s13 = p.element(frozenset({1, 3}))
        s23 = p.element(frozenset({2, 3}))
        s123 = p.element(frozenset({1, 2, 3}))
        
        # Test commutativity
        assert (s1 & s2) == (s2 & s1)
        assert (s1 | s2) == (s2 | s1)
        
        # Test associativity
        assert ((s1 & s2) & s3) == (s1 & (s2 & s3))
        assert ((s1 | s2) | s3) == (s1 | (s2 | s3))
        
        # Test absorption
        assert (s1 & (s1 | s2)) == s1
        assert (s1 | (s1 & s2)) == s1
        
        # Test idempotence
        assert (s1 & s1) == s1
        assert (s1 | s1) == s1
        
        # Test distributivity
        assert (s1 & (s2 | s3)) == ((s1 & s2) | (s1 & s3))
        assert (s1 | (s2 & s3)) == ((s1 | s2) & (s1 | s3))
        
        # Test identity elements
        assert (s1 & s123) == s1  # s123 is identity for meet
        assert (s1 | empty) == s1  # empty is identity for join
    
    def test_mixing_raw_and_wrapped_values(self, diamond_poset):
        """Test mixing raw values and wrapped elements in operations."""
        lattice = FiniteLattice(
            diamond_poset._elements, 
            [(x, y) for x in diamond_poset._elements for y in diamond_poset._elements 
             if diamond_poset.__le__(x, y)]
        )
        
        # Create some wrapped elements
        a = lattice.element("a")
        b = lattice.element("b")
        
        # Test operations mixing raw and wrapped values
        
        # Meet/join with raw values
        assert (a & "b").value == lattice.meet("a", "b")
        assert (a | "b").value == lattice.join("a", "b")
        
        # Comparisons with raw values
        assert ("0" < a) == lattice.__lt__("0", "a")
        assert (a > "0") == lattice.__gt__("a", "0")
        assert ("a" <= a) == lattice.__le__("a", "a")
        assert (a >= "a") == lattice.__ge__("a", "a")
        
        # Test lattice operations should work with either wrapped or raw values
        assert lattice.meet(a, "b") == lattice.meet("a", "b")
        assert lattice.join(a, "b") == lattice.join("a", "b")
        assert lattice.__le__(a, "1") == lattice.__le__("a", "1")
    
    def test_element_representation(self):
        """Test string and repr methods for lattice elements."""
        p = powerset_lattice({1, 2})
        
        # Create a wrapped element
        s1 = p.element(frozenset({1}))
        
        # Test string representation
        assert str(s1) == str(frozenset({1}))
        
        # Test repr
        assert repr(s1) == f"LatticeElement({repr(frozenset({1}))})"
    
    def test_custom_hash_function(self):
        """Test using a custom hash function for lattice elements."""
        p = powerset_lattice({1, 2, 3})
        
        # Define a custom hash function that just uses the length of the set
        def set_length_hash(s):
            return len(s)
        
        # Create elements with the custom hash function
        s1 = p.element(frozenset({1}), hash_function=set_length_hash)
        s2 = p.element(frozenset({2}), hash_function=set_length_hash)
        s3 = p.element(frozenset({3}), hash_function=set_length_hash)
        
        # Elements with same-sized sets should have same hash
        assert hash(s1) == hash(s2)
        assert hash(s1) == hash(s3)
        
        # Set global hash function for the lattice
        p.set_hash_function(set_length_hash)
        
        # New elements should use the lattice's hash function
        s12 = p.element(frozenset({1, 2}))
        s13 = p.element(frozenset({1, 3}))
        
        # Elements with same-sized sets should have same hash
        assert hash(s12) == hash(s13)
        
        # Different sized sets should have different hashes
        assert hash(s1) != hash(s12)
    
    def test_sublattice_compatibility(self):
        """Test that elements from a sublattice are compatible with the parent lattice."""
        # Create a lattice
        full_elements = ["0", "a", "b", "c", "1"]
        full_covers = [
            ("0", "a"), ("0", "b"), ("0", "c"),
            ("a", "1"), ("b", "1"), ("c", "1")
        ]
        full_lattice = FiniteLattice.from_cover_relations(full_elements, full_covers)
        
        # Create a sublattice (removing element "c")
        sub_elements = ["0", "a", "b", "1"]
        sub_covers = [
            ("0", "a"), ("0", "b"),
            ("a", "1"), ("b", "1")
        ]
        sub_lattice = FiniteLattice.from_cover_relations(sub_elements, sub_covers)
        
        # Verify sublattice relationship
        assert sub_lattice.is_sublattice_of(full_lattice)
        
        # Create elements from both lattices
        full_a = full_lattice.element("a")
        sub_a = sub_lattice.element("a")
        
        # Elements should be equal despite being from different lattices
        assert full_a == sub_a
        
        # Should be able to compare elements
        assert sub_a < full_lattice.element("1")
        assert full_lattice.element("0") < sub_a
        
        # Operations between elements should work
        assert (sub_a | full_lattice.element("b")).value == "1"
        assert (sub_a & full_lattice.element("b")).value == "0"
    
    def test_inheritance_from_parent_lattice(self, diamond_poset):
        """Test that lattice elements inherit semantics from their parent lattice."""
        lattice = FiniteLattice(
            diamond_poset._elements, 
            [(x, y) for x in diamond_poset._elements for y in diamond_poset._elements 
             if diamond_poset.__le__(x, y)]
        )
        
        # Create a modified version of the lattice with different semantics
        # We'll create a dual lattice where the ordering is reversed
        dual_lattice = lattice.dual()
        
        # Create elements from both lattices
        a = lattice.element("a")
        b = lattice.element("b")
        
        dual_a = dual_lattice.element("a")
        dual_b = dual_lattice.element("b")
        
        # Check that comparison semantics match the parent lattice
        # In original: a and b are incomparable
        assert not (a < b)
        assert not (a > b)
        
        # In dual: a and b are still incomparable
        assert not (dual_a < dual_b)
        assert not (dual_a > dual_b)
        
        # In original: meet(a, b) = "0", join(a, b) = "1"
        assert (a & b).value == "0"
        assert (a | b).value == "1"
        
        # In dual: meet and join are swapped
        # meet_dual(a, b) = "1", join_dual(a, b) = "0"
        assert (dual_a & dual_b).value == "1"
        assert (dual_a | dual_b).value == "0"
        
        # Verify that element operations always invoke the parent lattice's methods
        assert (a & b).value == lattice.meet("a", "b")
        assert (a | b).value == lattice.join("a", "b")
        assert (dual_a & dual_b).value == dual_lattice.meet("a", "b")
        assert (dual_a | dual_b).value == dual_lattice.join("a", "b")
