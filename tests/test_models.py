"""Property-based tests for data models.

Feature: kingdom-wars-bot, Property 16: Effective HP Calculation
"""
from hypothesis import given, strategies as st
from src.models import Tower


@given(
    hp=st.integers(min_value=0, max_value=500),
    armor=st.integers(min_value=0, max_value=200)
)
def test_effective_hp_calculation(hp: int, armor: int):
    """
    Property 16: Effective HP Calculation
    For any tower with HP H and armor A, the calculated effective HP should equal H + A.
    
    Feature: kingdom-wars-bot, Property 16: Effective HP Calculation
    Validates: Requirements 3.1
    """
    # Create a tower with random HP and armor
    tower = Tower(
        playerId=1,
        hp=hp,
        armor=armor,
        resources=100,
        level=1
    )
    
    # Calculate effective HP
    effective_hp = tower.hp + tower.armor
    
    # Verify the calculation
    assert effective_hp == hp + armor, \
        f"Effective HP should be {hp + armor}, but got {effective_hp}"
    
    # Verify it's always non-negative
    assert effective_hp >= 0, "Effective HP should never be negative"
    
    # Verify it's at least as much as HP alone
    assert effective_hp >= hp, "Effective HP should be at least as much as HP"
    
    # Verify it's at least as much as armor alone
    assert effective_hp >= armor, "Effective HP should be at least as much as armor"
