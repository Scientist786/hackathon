"""Target selection logic for Kingdom Wars Bot."""
from typing import List, Optional
from src.models import Tower


class TargetSelector:
    """Intelligently selects attack targets based on game state."""
    
    @staticmethod
    def filter_alive_towers(towers: List[Tower]) -> List[Tower]:
        """
        Filter out destroyed towers (HP ≤ 0).
        
        This is CRITICAL - never attack destroyed towers as it wastes resources.
        """
        return [tower for tower in towers if tower.hp > 0]
    
    @staticmethod
    def calculate_effective_hp(tower: Tower) -> int:
        """
        Calculate effective HP (total damage needed to destroy tower).
        
        Effective HP = HP + Armor
        """
        return tower.hp + tower.armor
    
    @staticmethod
    def find_weakest_tower(towers: List[Tower]) -> Optional[Tower]:
        """
        Find the weakest tower (lowest effective HP) among alive towers.
        
        Returns None if no alive towers exist.
        """
        alive_towers = TargetSelector.filter_alive_towers(towers)
        if not alive_towers:
            return None
        
        return min(alive_towers, key=TargetSelector.calculate_effective_hp)
    
    @staticmethod
    def find_strongest_tower(towers: List[Tower]) -> Optional[Tower]:
        """
        Find the strongest tower based on level and effective HP.
        
        Strength metric: (level * 100) + effective_hp
        This prioritizes high-level towers as they generate more resources.
        
        Returns None if no alive towers exist.
        """
        alive_towers = TargetSelector.filter_alive_towers(towers)
        if not alive_towers:
            return None
        
        def strength_metric(tower: Tower) -> int:
            return (tower.level * 100) + TargetSelector.calculate_effective_hp(tower)
        
        return max(alive_towers, key=strength_metric)
    
    @staticmethod
    def should_attack_target(target: Tower, our_resources: int) -> bool:
        """
        Determine if attacking a target is worthwhile.
        
        Attack is worthwhile if:
        1. Target is alive (HP > 0)
        2. We can deal meaningful damage (> 20% of effective HP)
        """
        if target.hp <= 0:
            return False
        
        effective_hp = TargetSelector.calculate_effective_hp(target)
        meaningful_damage_threshold = effective_hp * 0.2
        
        return our_resources >= meaningful_damage_threshold
    
    @staticmethod
    def rank_targets_by_priority(
        towers: List[Tower],
        our_resources: int,
        prioritize_elimination: bool = False
    ) -> List[Tower]:
        """
        Rank targets by attack priority.
        
        If prioritize_elimination is True (late game/fatigue):
            - Prioritize weakest towers that can be eliminated
        
        Otherwise (early/mid game):
            - Prioritize weakest towers to reduce threats
        
        Returns list sorted by priority (highest priority first).
        """
        alive_towers = TargetSelector.filter_alive_towers(towers)
        
        if not alive_towers:
            return []
        
        if prioritize_elimination:
            # Sort by effective HP (ascending) - easiest to eliminate first
            return sorted(alive_towers, key=TargetSelector.calculate_effective_hp)
        else:
            # Sort by effective HP (ascending) - weakest first
            return sorted(alive_towers, key=TargetSelector.calculate_effective_hp)
    
    @staticmethod
    def find_second_strongest_tower(towers: List[Tower]) -> Optional[Tower]:
        """
        Find the second strongest tower.
        
        Useful for alliance formation - ally with 2nd strongest to attack 1st.
        """
        alive_towers = TargetSelector.filter_alive_towers(towers)
        if len(alive_towers) < 2:
            return None
        
        def strength_metric(tower: Tower) -> int:
            return (tower.level * 100) + TargetSelector.calculate_effective_hp(tower)
        
        sorted_towers = sorted(alive_towers, key=strength_metric, reverse=True)
        return sorted_towers[1]  # Return second strongest
