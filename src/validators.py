"""Action validation logic for Kingdom Wars Bot."""
from typing import List, Dict, Set
from src.models import CombatAction, ArmorAction, AttackAction, UpgradeAction


class ValidationResult:
    """Result of action validation."""
    
    def __init__(self, valid: bool = True, errors: List[str] = None, total_cost: int = 0):
        self.valid = valid
        self.errors = errors or []
        self.total_cost = total_cost
    
    def add_error(self, error: str):
        """Add an error to the validation result."""
        self.valid = False
        self.errors.append(error)


class ActionValidator:
    """Validates combat actions against game rules."""
    
    @staticmethod
    def calculate_armor_cost(amount: int) -> int:
        """
        Calculate cost of armor action.
        Cost: amount × 1 resource
        """
        return amount * 1
    
    @staticmethod
    def calculate_attack_cost(troop_count: int) -> int:
        """
        Calculate cost of attack action.
        Cost: troopCount × 1 resource
        """
        return troop_count * 1
    
    @staticmethod
    def calculate_upgrade_cost(current_level: int) -> int:
        """
        Calculate cost of upgrade action.
        Cost: 50 × (1.75 ^ (level - 1))
        
        Level 1→2: 50 resources
        Level 2→3: 88 resources (87.5 rounded)
        Level 3→4: 153 resources (153.125 rounded)
        Level 4→5: 268 resources (267.96875 rounded)
        Level 5→6: 469 resources (468.9453125 rounded)
        """
        if current_level >= 6:
            return float('inf')  # Cannot upgrade beyond level 6
        
        cost = 50 * (1.75 ** (current_level - 1))
        return round(cost)
    
    @staticmethod
    def calculate_action_cost(action: CombatAction, level: int) -> int:
        """Calculate the cost of a single action."""
        if isinstance(action, ArmorAction):
            return ActionValidator.calculate_armor_cost(action.amount)
        elif isinstance(action, AttackAction):
            return ActionValidator.calculate_attack_cost(action.troopCount)
        elif isinstance(action, UpgradeAction):
            return ActionValidator.calculate_upgrade_cost(level)
        return 0
    
    @staticmethod
    def has_multiple_armor(actions: List[CombatAction]) -> bool:
        """Check if there are multiple armor actions."""
        armor_count = sum(1 for action in actions if isinstance(action, ArmorAction))
        return armor_count > 1
    
    @staticmethod
    def has_multiple_upgrades(actions: List[CombatAction]) -> bool:
        """Check if there are multiple upgrade actions."""
        upgrade_count = sum(1 for action in actions if isinstance(action, UpgradeAction))
        return upgrade_count > 1
    
    @staticmethod
    def has_duplicate_targets(actions: List[CombatAction]) -> bool:
        """Check if there are duplicate attack targets."""
        attack_targets: Set[int] = set()
        for action in actions:
            if isinstance(action, AttackAction):
                if action.targetId in attack_targets:
                    return True
                attack_targets.add(action.targetId)
        return False
    
    @staticmethod
    def validate_combat_actions(
        actions: List[CombatAction],
        resources: int,
        level: int
    ) -> ValidationResult:
        """
        Validate a list of combat actions against game rules.
        
        Rules:
        - At most one armor action
        - At most one upgrade action
        - No duplicate attack targets
        - Total cost must not exceed available resources
        """
        result = ValidationResult()
        
        # Check for multiple armor actions
        if ActionValidator.has_multiple_armor(actions):
            result.add_error("Only one armor action allowed per combat phase")
        
        # Check for multiple upgrade actions
        if ActionValidator.has_multiple_upgrades(actions):
            result.add_error("Only one upgrade action allowed per combat phase")
        
        # Check for duplicate attack targets
        if ActionValidator.has_duplicate_targets(actions):
            result.add_error("Multiple attacks with identical targetId not allowed")
        
        # Calculate total cost
        total_cost = 0
        for action in actions:
            cost = ActionValidator.calculate_action_cost(action, level)
            total_cost += cost
        
        result.total_cost = total_cost
        
        # Check resource constraint
        if total_cost > resources:
            result.add_error(
                f"Total action cost ({total_cost}) exceeds available resources ({resources})"
            )
        
        return result
