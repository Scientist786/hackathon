"""Resource calculation logic for Kingdom Wars Bot."""


class ResourceCalculator:
    """Calculates resource generation and management."""
    
    BASE_GENERATION = 20
    GROWTH_MULTIPLIER = 1.5
    
    @staticmethod
    def calculate_resource_generation(level: int) -> int:
        """
        Calculate resource generation per turn based on tower level.
        
        Formula: 20 × (1.5 ^ (level - 1))
        
        Level 1: 20 resources/turn
        Level 2: 30 resources/turn
        Level 3: 45 resources/turn
        Level 4: 68 resources/turn (67.5 → 68)
        Level 5: 101 resources/turn (101.25 → 101)
        Level 6: 152 resources/turn (151.875 → 152)
        """
        if level < 1:
            return 0
        
        generation = ResourceCalculator.BASE_GENERATION * (
            ResourceCalculator.GROWTH_MULTIPLIER ** (level - 1)
        )
        return round(generation)
    
    @staticmethod
    def calculate_next_turn_resources(current_resources: int, level: int, spent: int = 0) -> int:
        """
        Calculate resources available next turn.
        
        Args:
            current_resources: Resources available now
            level: Current tower level
            spent: Resources to be spent this turn
        
        Returns:
            Resources available next turn
        """
        remaining = current_resources - spent
        generation = ResourceCalculator.calculate_resource_generation(level)
        return remaining + generation
    
    @staticmethod
    def can_afford_upgrade(resources: int, level: int) -> bool:
        """
        Check if we can afford to upgrade.
        
        Uses the upgrade cost formula from ActionValidator.
        """
        from src.validators import ActionValidator
        upgrade_cost = ActionValidator.calculate_upgrade_cost(level)
        return resources >= upgrade_cost
    
    @staticmethod
    def turns_to_afford_upgrade(current_resources: int, level: int) -> int:
        """
        Calculate how many turns until we can afford an upgrade.
        
        Returns 0 if we can already afford it.
        Returns -1 if we're at max level.
        """
        if level >= 6:
            return -1  # Max level reached
        
        from src.validators import ActionValidator
        upgrade_cost = ActionValidator.calculate_upgrade_cost(level)
        
        if current_resources >= upgrade_cost:
            return 0
        
        needed = upgrade_cost - current_resources
        generation_per_turn = ResourceCalculator.calculate_resource_generation(level)
        
        if generation_per_turn <= 0:
            return 999  # Can't afford it
        
        turns = (needed + generation_per_turn - 1) // generation_per_turn  # Ceiling division
        return turns
    
    @staticmethod
    def calculate_upgrade_roi(level: int) -> float:
        """
        Calculate return on investment for upgrading.
        
        ROI = (new_generation - old_generation) / upgrade_cost
        
        Higher ROI means upgrade pays for itself faster.
        """
        if level >= 6:
            return 0.0  # Can't upgrade
        
        from src.validators import ActionValidator
        
        current_generation = ResourceCalculator.calculate_resource_generation(level)
        next_generation = ResourceCalculator.calculate_resource_generation(level + 1)
        upgrade_cost = ActionValidator.calculate_upgrade_cost(level)
        
        if upgrade_cost == 0:
            return float('inf')
        
        additional_generation = next_generation - current_generation
        roi = additional_generation / upgrade_cost
        
        return roi
