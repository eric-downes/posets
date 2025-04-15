"""
Pytest configuration for posets library tests.
"""
import pytest
from typing import Dict, List, Set, FrozenSet, Any, Tuple, Optional

# These fixtures will be available to all tests
@pytest.fixture
def diamond_poset():
    """Fixture that returns a diamond-shaped poset (M3 lattice)."""
    from posets.core.finite_poset import FinitePoset
    
    elements = ["0", "a", "b", "c", "1"]
    covers = [
        ("0", "a"), ("0", "b"), ("0", "c"),
        ("a", "1"), ("b", "1"), ("c", "1")
    ]
    return FinitePoset.from_cover_relations(elements, covers)

@pytest.fixture
def pentagon_poset():
    """Fixture that returns the pentagon poset (N5 lattice)."""
    from posets.core.finite_poset import FinitePoset
    
    elements = ["0", "a", "b", "c", "1"]
    covers = [
        ("0", "a"), ("0", "b"),
        ("a", "c"),
        ("b", "1"),
        ("c", "1")
    ]
    return FinitePoset.from_cover_relations(elements, covers)

@pytest.fixture
def boolean_3_lattice():
    """Fixture that returns the Boolean lattice of dimension 3."""
    from posets.core.factories import boolean_lattice
    return boolean_lattice(3)

@pytest.fixture
def divisor_lattice_30():
    """Fixture that returns the lattice of divisors of 30."""
    from posets.core.factories import divisor_lattice
    return divisor_lattice(30)  # Divisors: 1, 2, 3, 5, 6, 10, 15, 30

@pytest.fixture
def complex_poset():
    """Fixture that returns a more complex poset for testing algorithms."""
    from posets.core.finite_poset import FinitePoset
    
    # Create a poset with multiple paths and interesting structure
    elements = list(range(10))
    covers = [
        (0, 1), (0, 2), (0, 3),
        (1, 4), (1, 5),
        (2, 5), (2, 6),
        (3, 6), (3, 7),
        (4, 8),
        (5, 8), (5, 9),
        (6, 9),
        (7, 9)
    ]
    return FinitePoset.from_cover_relations(elements, covers)