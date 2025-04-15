"""
Tests for lattice functionality.
"""
import pytest
from typing import List, Set, FrozenSet, Any, Optional

# These imports will work once we implement the actual code
# For now, they serve as a syntax guide for the implementation
from posets.core.finite_poset import FinitePoset
from posets.lattice.base import FiniteLattice
from posets.core.factories import chain, antichain, powerset_lattice, boolean_lattice, divisor_lattice


class TestLatticeOperations:
    """Tests for basic lattice operations like meet and join."""
    
    def test_meet_in_powerset(self):
        """Test that meet operation computes set intersection in a powerset lattice."""
        p = powerset_lattice({1, 2, 3})
        
        # Element representations as frozensets
        s1 = frozenset({1, 2})
        s2 = frozenset({2, 3})
        
        # Meet should be set intersection
        result = p.meet(s1, s2)
        assert result == frozenset({2})
    
    def test_join_in_powerset(self):
        """Test that join operation computes set union in a powerset lattice."""
        p = powerset_lattice({1, 2, 3})
        
        # Element representations as frozensets
        s1 = frozenset({1, 2})
        s2 = frozenset({2, 3})
        
        # Join should be set union
        result = p.join(s1, s2)
        assert result == frozenset({1, 2, 3})
    
    def test_meet_in_divisor_lattice(self):
        """Test that meet computes GCD in a divisor lattice."""
        d = divisor_lattice(60)  # Divisors of 60: 1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30, 60
        
        # Meet should be greatest common divisor
        assert d.meet(12, 20) == 4  # gcd(12, 20) = 4
        assert d.meet(15, 20) == 5  # gcd(15, 20) = 5
        assert d.meet(30, 20) == 10  # gcd(30, 20) = 10
    
    def test_join_in_divisor_lattice(self):
        """Test that join computes LCM in a divisor lattice."""
        d = divisor_lattice(60)  # Divisors of 60: 1, 2, 3, 4, 5, 6, 10, 12, 15, 20, 30, 60
        
        # Join should be least common multiple
        assert d.join(12, 20) == 60  # lcm(12, 20) = 60
        assert d.join(6, 10) == 30  # lcm(6, 10) = 30
        assert d.join(4, 15) == 60  # lcm(4, 15) = 60
    
    def test_meet_join_properties(self):
        """Test algebraic properties of meet and join operations."""
        # Use Boolean lattice as a test case
        b = boolean_lattice(3)
        
        for x in list(b.elements())[:4]:  # Use first few elements to keep test fast
            for y in list(b.elements())[:4]:
                # Commutativity
                assert b.meet(x, y) == b.meet(y, x)
                assert b.join(x, y) == b.join(y, x)
                
                # Idempotence
                assert b.meet(x, x) == x
                assert b.join(x, x) == x
                
                # Absorption
                assert b.meet(x, b.join(x, y)) == x
                assert b.join(x, b.meet(x, y)) == x
                
                for z in list(b.elements())[:4]:
                    # Associativity
                    assert b.meet(x, b.meet(y, z)) == b.meet(b.meet(x, y), z)
                    assert b.join(x, b.join(y, z)) == b.join(b.join(x, y), z)
    
    def test_supremum_infimum(self):
        """Test computation of supremum and infimum for sets of elements."""
        p = powerset_lattice({1, 2, 3})
        
        # Prepare some elements
        empty = frozenset()
        s1 = frozenset({1})
        s2 = frozenset({2})
        s3 = frozenset({3})
        
        # Test infimum (intersection of all sets)
        elements = [s1, s2, s3]
        assert p.infimum(elements) == empty
        
        # Test supremum (union of all sets)
        assert p.supremum(elements) == frozenset({1, 2, 3})
        
        # Test with different elements
        elements = [frozenset({1, 2}), frozenset({2, 3})]
        assert p.infimum(elements) == frozenset({2})
        assert p.supremum(elements) == frozenset({1, 2, 3})
        
        # Test empty set of elements should return None
        assert p.infimum([]) is None
        assert p.supremum([]) is None
    
    def test_chain_is_lattice(self):
        """Test that a chain forms a lattice where meet/join are min/max."""
        c = FiniteLattice(list(range(5)), [(i, j) for i in range(5) for j in range(5) if i <= j])
        
        # In a chain, meet is minimum and join is maximum
        assert c.meet(1, 3) == 1
        assert c.join(1, 3) == 3
        
        # Test with different elements
        assert c.meet(2, 4) == 2
        assert c.join(2, 4) == 4
        
        # Test with same element
        assert c.meet(2, 2) == 2
        assert c.join(2, 2) == 2


class TestLatticeConstructors:
    """Tests for lattice construction from different inputs."""
    
    def test_lattice_from_poset(self):
        """Test construction of a lattice from poset relations."""
        # Define a diamond lattice: bottom < a, b < top
        elements = ["bottom", "a", "b", "top"]
        relation = [
            ("bottom", "bottom"), ("a", "a"), ("b", "b"), ("top", "top"),  # Reflexive
            ("bottom", "a"), ("bottom", "b"), ("a", "top"), ("b", "top"),  # Covers
            ("bottom", "top")  # Transitive
        ]
        
        l = FiniteLattice(elements, relation)
        
        # Test the structure was correctly built
        assert l.__le__("bottom", "top")
        assert l.__le__("a", "top")
        assert not l.__le__("a", "b")
        
        # Test meet and join
        assert l.meet("a", "b") == "bottom"
        assert l.join("a", "b") == "top"
    
    def test_error_on_non_lattice(self):
        """Test that lattice constructor raises error if the poset is not a lattice."""
        # Define a "V" shape poset which is not a lattice (no join for the two upper elements)
        # a   b
        #  \ /
        #   c
        elements = ["a", "b", "c"]
        relation = [
            ("a", "a"), ("b", "b"), ("c", "c"),  # Reflexive
            ("c", "a"), ("c", "b")  # c is below a and b
        ]
        
        # This should raise an error because a and b have no least upper bound
        with pytest.raises(ValueError):
            FiniteLattice(elements, relation)
    
    def test_boolean_lattice_construction(self):
        """Test the boolean lattice factory function creates a proper structure."""
        b = boolean_lattice(3)  # 2³ = 8 elements
        
        # Test structure has correct number of elements
        assert len(list(b.elements())) == 8
        
        # Test it has a unique bottom and top
        bottoms = list(b.minimal_elements())
        tops = list(b.maximal_elements())
        assert len(bottoms) == 1
        assert len(tops) == 1
        
        # Bottom should be empty set
        assert bottoms[0] == frozenset()
        
        # Top should have all elements
        assert tops[0] == frozenset({0, 1, 2})
        
        # Test complementation - in a Boolean lattice, every element has a complement
        for x in b.elements():
            # Complement elements that are in the top but not in x
            complement_contents = tops[0].difference(x)
            complement = frozenset(complement_contents)
            
            # Meet of element and complement should be bottom
            assert b.meet(x, complement) == bottoms[0]
            
            # Join of element and complement should be top
            assert b.join(x, complement) == tops[0]
    
    def test_divisor_lattice_construction(self):
        """Test the divisor lattice factory creates a proper structure."""
        d = divisor_lattice(12)  # Divisors: 1, 2, 3, 4, 6, 12
        
        # Test structure has correct elements
        assert set(d.elements()) == {1, 2, 3, 4, 6, 12}
        
        # Test it has a unique bottom (1) and top (n)
        assert list(d.minimal_elements()) == [1]
        assert list(d.maximal_elements()) == [12]
        
        # Test cover relationships
        assert set(d.upper_covers(1)) == {2, 3}
        assert set(d.upper_covers(2)) == {4, 6}
        assert set(d.upper_covers(3)) == {6}
        assert set(d.upper_covers(4)) == {12}
        assert set(d.upper_covers(6)) == {12}


class TestBoundedLattice:
    """Tests for bounded lattice functionality (lattices with top and bottom elements)."""
    
    def test_top_bottom_in_powerset(self):
        """Test identification of top and bottom elements in a powerset lattice."""
        p = powerset_lattice({1, 2, 3})
        
        # Test top property (should be the full set)
        assert p.top == frozenset({1, 2, 3})
        
        # Test bottom property (should be the empty set)
        assert p.bottom == frozenset()
    
    def test_top_bottom_in_divisor_lattice(self):
        """Test identification of top and bottom elements in a divisor lattice."""
        d = divisor_lattice(30)
        
        # Test top property (should be n itself)
        assert d.top == 30
        
        # Test bottom property (should be 1)
        assert d.bottom == 1
    
    def test_bounded_lattice_properties(self):
        """Test properties of top and bottom elements in a bounded lattice."""
        b = boolean_lattice(3)
        
        # Top is the greatest element
        for x in b.elements():
            assert b.__le__(x, b.top)
            assert b.join(x, b.top) == b.top
            assert b.meet(x, b.top) == x
        
        # Bottom is the least element
        for x in b.elements():
            assert b.__le__(b.bottom, x)
            assert b.join(x, b.bottom) == x
            assert b.meet(x, b.bottom) == b.bottom


class TestDualLattice:
    """Tests for dual lattice construction (flipping the order relation)."""
    
    def test_dual_meets_and_joins(self):
        """Test that meet and join are swapped in the dual lattice."""
        l = powerset_lattice({1, 2})
        dual_l = l.dual()
        
        # Meet in original is join in dual, and vice versa
        s1 = frozenset({1})
        s2 = frozenset({2})
        
        original_meet = l.meet(s1, s2)  # Empty set
        original_join = l.join(s1, s2)  # {1, 2}
        
        dual_meet = dual_l.meet(s1, s2)
        dual_join = dual_l.join(s1, s2)
        
        assert dual_meet == original_join
        assert dual_join == original_meet
    
    def test_dual_order_relation(self):
        """Test that the order relation is flipped in the dual lattice."""
        l = chain(5)  # 0 < 1 < 2 < 3 < 4
        dual_l = l.dual()  # 4 < 3 < 2 < 1 < 0
        
        # Original order
        assert l.__le__(0, 4)
        assert not l.__le__(4, 0)
        
        # Dual order should be flipped
        assert dual_l.__le__(4, 0)
        assert not dual_l.__le__(0, 4)
        
        # Test minimal and maximal elements are swapped
        assert list(l.minimal_elements()) == [0]
        assert list(l.maximal_elements()) == [4]
        
        assert list(dual_l.minimal_elements()) == [4]
        assert list(dual_l.maximal_elements()) == [0]