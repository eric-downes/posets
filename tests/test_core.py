"""
Tests for core poset functionality.
"""
import pytest
from typing import List, Set, FrozenSet, Any

# These imports will work once we implement the actual code
# For now, they serve as a syntax guide for the implementation
from posets.core.finite_poset import FinitePoset
from posets.core.factories import chain, antichain, powerset_lattice

class TestPosetComparisons:
    """Tests for basic poset comparison operations."""
    
    def test_chain_comparisons(self):
        """Test that chain elements are properly ordered and comparable."""
        c = chain(5)  # Chain with 5 elements: 0 < 1 < 2 < 3 < 4
        
        # Test less than or equal
        assert c.__le__(0, 0)  # Reflexivity
        assert c.__le__(0, 1)  # Adjacent elements
        assert c.__le__(0, 4)  # Transitive comparison
        assert not c.__le__(4, 0)  # Non-comparable in this direction
        
        # Test strictly less than
        assert not c.__lt__(0, 0)  # Not strictly less than itself
        assert c.__lt__(0, 1)  # Adjacent elements
        assert c.__lt__(0, 4)  # Transitive comparison
        assert not c.__lt__(4, 0)  # Non-comparable in this direction
        
        # Test greater than or equal (derived from __le__)
        assert c.__ge__(4, 4)  # Reflexivity
        assert c.__ge__(4, 0)  # Transitive comparison
        assert not c.__ge__(0, 4)  # Non-comparable in this direction
        
        # Test strictly greater than (derived from __lt__)
        assert not c.__gt__(4, 4)  # Not strictly greater than itself
        assert c.__gt__(4, 0)  # Transitive comparison
        assert not c.__gt__(0, 4)  # Non-comparable in this direction
        
        # Test comparability
        assert c.is_comparable(0, 4)  # All elements in a chain are comparable
        assert c.is_comparable(4, 0)  # Comparability is symmetric

    def test_antichain_comparisons(self):
        """Test that antichain elements are only comparable to themselves."""
        elements = ['a', 'b', 'c', 'd']
        a = antichain(elements)
        
        # Test less than or equal - only reflexive pairs
        assert a.__le__('a', 'a')  # Reflexivity
        assert not a.__le__('a', 'b')  # No other comparisons
        
        # Test strictly less than - no pairs
        assert not a.__lt__('a', 'a')  # Not strictly less than itself
        assert not a.__lt__('a', 'b')  # No comparisons between different elements
        
        # Test comparability
        assert a.is_comparable('a', 'a')  # Element is comparable to itself
        assert not a.is_comparable('a', 'b')  # Different elements are not comparable
    
    def test_powerset_comparisons(self):
        """Test that powerset elements are ordered by inclusion."""
        p = powerset_lattice({1, 2, 3})
        
        # Test subset relationships
        empty = frozenset()
        s1 = frozenset({1})
        s2 = frozenset({2})
        s12 = frozenset({1, 2})
        s123 = frozenset({1, 2, 3})
        
        # Test less than or equal (subset relationship)
        assert p.__le__(empty, s1)  # Empty set is subset of all sets
        assert p.__le__(s1, s12)  # {1} is subset of {1,2}
        assert p.__le__(s12, s123)  # {1,2} is subset of {1,2,3}
        assert not p.__le__(s1, s2)  # {1} is not subset of {2}
        
        # Test strictly less than (proper subset)
        assert p.__lt__(empty, s1)  # Empty set is proper subset of non-empty sets
        assert p.__lt__(s1, s123)  # {1} is proper subset of {1,2,3}
        assert not p.__lt__(s1, s1)  # Not strictly less than itself
        
        # Test comparability - sets are comparable if one is subset of the other
        assert p.is_comparable(s1, s12)  # One is subset of the other
        assert not p.is_comparable(s1, s2)  # Neither is subset of the other


class TestPosetOperations:
    """Tests for basic poset operations and queries."""
    
    def test_cover_relations(self):
        """Test that cover relations correctly identify immediate successors/predecessors."""
        # Test in a chain
        c = chain(5)  # 0 < 1 < 2 < 3 < 4
        
        # Test covers method
        assert c.covers(1, 0)  # 1 covers 0
        assert not c.covers(2, 0)  # 2 does not cover 0 (not immediate)
        
        # Test upper_covers method
        assert set(c.upper_covers(0)) == {1}  # 0 is covered by 1
        assert set(c.upper_covers(3)) == {4}  # 3 is covered by 4
        
        # Test lower_covers method
        assert set(c.lower_covers(4)) == {3}  # 4 covers 3
        assert set(c.lower_covers(0)) == set()  # 0 has no lower covers
        
        # Test in a more complex poset - divisor lattice of 12
        elements = [1, 2, 3, 4, 6, 12]
        covers = [(1, 2), (1, 3), (2, 4), (2, 6), (3, 6), (4, 12), (6, 12)]
        p = FinitePoset.from_cover_relations(elements, covers)
        
        # Test upper_covers
        assert set(p.upper_covers(1)) == {2, 3}
        assert set(p.upper_covers(2)) == {4, 6}
        assert set(p.upper_covers(4)) == {12}
        
        # Test lower_covers
        assert set(p.lower_covers(12)) == {4, 6}
        assert set(p.lower_covers(6)) == {2, 3}
        assert set(p.lower_covers(1)) == set()
    
    def test_minimal_maximal_elements(self):
        """Test identification of minimal and maximal elements in a poset."""
        # Test in a chain - single minimal and maximal element
        c = chain(5)  # 0 < 1 < 2 < 3 < 4
        assert set(c.minimal_elements()) == {0}
        assert set(c.maximal_elements()) == {4}
        
        # Test in an antichain - all elements are both minimal and maximal
        elements = ['a', 'b', 'c', 'd']
        a = antichain(elements)
        assert set(a.minimal_elements()) == set(elements)
        assert set(a.maximal_elements()) == set(elements)
        
        # Test in a more complex poset - "N" shape
        elements = [1, 2, 3, 4, 5]
        covers = [(1, 2), (1, 3), (2, 4), (3, 5)]
        # Looks like:
        #   4   5
        #   |   |
        #   2   3
        #    \ /
        #     1
        p = FinitePoset.from_cover_relations(elements, covers)
        assert set(p.minimal_elements()) == {1}
        assert set(p.maximal_elements()) == {4, 5}


class TestPosetConstructors:
    """Tests for poset construction from different inputs."""
    
    def test_from_relation(self):
        """Test construction of a poset from a binary relation."""
        elements = [1, 2, 3, 4]
        # Define a relation: 1 ≤ 2 ≤ 4 and 1 ≤ 3 ≤ 4
        relation = [(1, 1), (2, 2), (3, 3), (4, 4),  # Reflexive pairs
                    (1, 2), (1, 3), (2, 4), (3, 4),  # Other pairs
                    (1, 4)]  # Transitive pair (will be inferred if not provided)
        
        p = FinitePoset(elements, relation)
        
        # Test the structure was correctly built
        assert p.__le__(1, 4)
        assert p.__le__(2, 4)
        assert p.__le__(3, 4)
        assert not p.__le__(2, 3)
        assert not p.__le__(3, 2)
        
        # Test cover relations were correctly extracted
        assert set(p.upper_covers(1)) == {2, 3}
        assert set(p.lower_covers(4)) == {2, 3}
    
    def test_from_cover_relations(self):
        """Test construction of a poset directly from cover relations."""
        elements = ['a', 'b', 'c', 'd', 'e']
        # Define a poset: a < b < d and a < c < e
        covers = [('a', 'b'), ('a', 'c'), ('b', 'd'), ('c', 'e')]
        
        p = FinitePoset.from_cover_relations(elements, covers)
        
        # Test the structure was correctly built
        assert p.__le__('a', 'd')  # Transitive relation
        assert p.__le__('a', 'e')  # Transitive relation
        assert not p.__le__('b', 'e')
        assert not p.__le__('c', 'd')
        
        # Test cover relations match what we provided
        assert set(p.upper_covers('a')) == {'b', 'c'}
        assert set(p.upper_covers('b')) == {'d'}
    
    def test_error_on_invalid_elements(self):
        """Test that operations on elements not in the poset raise errors."""
        p = chain(5)
        
        with pytest.raises(ValueError):
            p.__le__(0, 10)  # 10 is not in the poset
        
        with pytest.raises(ValueError):
            p.__lt__(10, 0)  # 10 is not in the poset
            
        with pytest.raises(ValueError):
            list(p.upper_covers(10))  # 10 is not in the poset
            
        with pytest.raises(ValueError):
            list(p.lower_covers(10))  # 10 is not in the poset


class TestPosetFactories:
    """Tests for built-in factory functions that create common posets."""
    
    def test_chain_factory(self):
        """Test the chain factory creates a totally ordered set."""
        c = chain(5)
        
        # Test structure has 5 elements
        assert len(list(c.elements())) == 5
        
        # Test all elements are comparable
        elements = list(c.elements())
        for i in range(len(elements)):
            for j in range(len(elements)):
                assert c.is_comparable(elements[i], elements[j])
        
        # Test the total ordering
        for i in range(len(elements) - 1):
            assert c.__lt__(elements[i], elements[i+1])
    
    def test_antichain_factory(self):
        """Test the antichain factory creates a discrete poset."""
        elements = [10, 20, 30, 40, 50]
        a = antichain(elements)
        
        # Test structure has the correct elements
        assert set(a.elements()) == set(elements)
        
        # Test no elements are comparable except to themselves
        for i in range(len(elements)):
            for j in range(len(elements)):
                if i == j:
                    assert a.__le__(elements[i], elements[j])
                else:
                    assert not a.__le__(elements[i], elements[j])
    
    def test_powerset_factory(self):
        """Test the powerset factory creates a lattice of subsets ordered by inclusion."""
        base_set = {1, 2, 3}
        p = powerset_lattice(base_set)
        
        # Test structure has 2^3 = 8 elements
        assert len(list(p.elements())) == 8
        
        # Check all subsets are present
        all_subsets = [frozenset(), 
                      frozenset({1}), frozenset({2}), frozenset({3}),
                      frozenset({1, 2}), frozenset({1, 3}), frozenset({2, 3}),
                      frozenset({1, 2, 3})]
        assert set(p.elements()) == set(all_subsets)
        
        # Test ordering by subset relation
        assert p.__le__(frozenset(), frozenset({1, 2, 3}))
        assert p.__le__(frozenset({1}), frozenset({1, 2}))
        assert not p.__le__(frozenset({1}), frozenset({2, 3}))