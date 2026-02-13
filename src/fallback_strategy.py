"""Fallback strategy when AI is unavailable."""
import logging
from typing import List
from src.models import (
    NegotiationRequest, CombatRequest, DiplomacyAction,
    CombatAction, ArmorAction, AttackAction, UpgradeAction, Tower
)
from src.targeting import TargetSelector
from src.fatigue import FatigueCalculator
from src.validators import ActionValidator
from src.resources import ResourceCalculator

logger = logging.getLogger(__name__)


class FallbackStrategy:
    """Provides intelligent rule-based strategies when AI is unavailable."""
    
    @staticmethod
    def generate_negotiation_actions(request: NegotiationRequest) -> List[DiplomacyAction]:
        """
        Generate negotiation actions using intelligent heuristics.
        
        Strategy:
        1. Identify strongest threat (highest level + effective HP)
        2. Form alliance with 2nd strongest player
        3. Declare attack on strongest opponent
        4. If we're strongest, ally with weakest to protect them
        """
        player = request.playerTower
        enemies = request.enemyTowers
        
        # Filter alive enemies
        alive_enemies = TargetSelector.filter_alive_towers(enemies)
        
        if not alive_enemies:
            return []
        
        # Find strongest and second strongest
        strongest = TargetSelector.find_strongest_tower(alive_enemies)
        second_strongest = TargetSelector.find_second_strongest_tower(alive_enemies)
        
        if not strongest:
            return []
        
        # Determine if we're the strongest
        our_strength = (player.level * 100) + TargetSelector.calculate_effective_hp(player)
        strongest_strength = (strongest.level * 100) + TargetSelector.calculate_effective_hp(strongest)
        
        actions = []
        
        if our_strength >= strongest_strength:
            # We're the strongest - ally with 2nd strongest or weakest
            if second_strongest:
                actions.append(DiplomacyAction(
                    allyId=second_strongest.playerId,
                    attackTargetId=None
                ))
        else:
            # We're not strongest - ally with 2nd strongest to attack leader
            if second_strongest and second_strongest.playerId != strongest.playerId:
                actions.append(DiplomacyAction(
                    allyId=second_strongest.playerId,
                    attackTargetId=strongest.playerId
                ))
            elif len(alive_enemies) >= 2:
                # Ally with anyone except strongest
                for enemy in alive_enemies:
                    if enemy.playerId != strongest.playerId:
                        actions.append(DiplomacyAction(
                            allyId=enemy.playerId,
                            attackTargetId=strongest.playerId
                        ))
                        break
        
        logger.info(f"Fallback negotiation: {len(actions)} diplomacy actions")
        return actions
    
    @staticmethod
    def generate_combat_actions(request: CombatRequest) -> List[CombatAction]:
        """
        Generate combat actions using intelligent winning heuristics.
        
        Strategy varies by game phase:
        
        EARLY GAME (Turns 1-10): Resource Growth
        - Upgrade to level 3-4 ASAP
        - Build armor only if HP < 60
        - Light attacks on weakest
        
        MID GAME (Turns 11-24): Dominance
        - Upgrade to level 4 if possible
        - Focus attacks on weakest to eliminate
        - Build armor to maintain HP > 50
        
        LATE GAME (Turns 25+): Survival & Elimination
        - Aggressive attacks (70-80% of resources)
        - Focus fire on weakest to eliminate
        - Minimal armor (only if HP < 30)
        - NO upgrades
        """
        turn = request.turn
        player = request.playerTower
        enemies = request.enemyTowers
        
        # Filter alive enemies
        alive_enemies = TargetSelector.filter_alive_towers(enemies)
        
        if not alive_enemies:
            logger.info("No alive enemies - no actions needed")
            return []
        
        actions: List[CombatAction] = []
        available_resources = player.resources
        game_phase = FatigueCalculator.get_fatigue_phase(turn)
        fatigue_active = FatigueCalculator.is_fatigue_active(turn)
        
        logger.info(f"Fallback combat: Turn {turn}, Phase {game_phase}, Resources {available_resources}")
        
        # Phase-specific strategy
        if game_phase == "early":
            actions = FallbackStrategy._early_game_strategy(
                player, alive_enemies, available_resources
            )
        elif game_phase == "mid":
            actions = FallbackStrategy._mid_game_strategy(
                player, alive_enemies, available_resources
            )
        else:  # late game
            actions = FallbackStrategy._late_game_strategy(
                player, alive_enemies, available_resources, turn
            )
        
        # Validate actions
        validation = ActionValidator.validate_combat_actions(actions, available_resources, player.level)
        if not validation.valid:
            logger.warning(f"Generated invalid actions: {validation.errors}")
            # Return empty array rather than invalid actions
            return []
        
        logger.info(f"Fallback generated {len(actions)} actions, cost {validation.total_cost}")
        return actions
    
    @staticmethod
    def _early_game_strategy(
        player: Tower,
        enemies: List[Tower],
        resources: int
    ) -> List[CombatAction]:
        """Early game strategy: Focus on upgrades and defense."""
        actions = []
        remaining = resources
        
        # Priority 1: Build armor if HP is low
        if player.hp < 70 and remaining >= 20:
            armor_amount = min(50, remaining)
            actions.append(ArmorAction(type="armor", amount=armor_amount))
            remaining -= armor_amount
        
        # Priority 2: Upgrade as much as possible
        if player.level < 5:
            upgrade_cost = ActionValidator.calculate_upgrade_cost(player.level)
            if remaining >= upgrade_cost:
                actions.append(UpgradeAction(type="upgrade"))
                remaining -= upgrade_cost
        
        # Priority 3: Minimal attacks (10-20% of remaining resources)
        if remaining >= 20:
            weakest = TargetSelector.find_weakest_tower(enemies)
            if weakest:
                attack_amount = min(remaining // 5, 20)  # Use 20% resources, max 20
                if attack_amount > 0:
                    actions.append(AttackAction(
                        type="attack",
                        targetId=weakest.playerId,
                        troopCount=attack_amount
                    ))
        
        return actions
    
    @staticmethod
    def _mid_game_strategy(
        player: Tower,
        enemies: List[Tower],
        resources: int
    ) -> List[CombatAction]:
        """Mid game strategy: Continue upgrades and maintain strong defense."""
        actions = []
        remaining = resources
        
        # Priority 1: Maintain armor buffer
        if player.hp < 60 and remaining >= 30:
            armor_amount = min(60, remaining)
            actions.append(ArmorAction(type="armor", amount=armor_amount))
            remaining -= armor_amount
        
        # Priority 2: Upgrade to max level
        if player.level < 5:
            upgrade_cost = ActionValidator.calculate_upgrade_cost(player.level)
            if remaining >= upgrade_cost:
                actions.append(UpgradeAction(type="upgrade"))
                remaining -= upgrade_cost
        
        # Priority 3: Light attacks (20-30% of remaining)
        if remaining >= 30:
            weakest = TargetSelector.find_weakest_tower(enemies)
            if weakest:
                attack_amount = int(remaining * 0.25)  # Use 25% of remaining
                if attack_amount > 0:
                    actions.append(AttackAction(
                        type="attack",
                        targetId=weakest.playerId,
                        troopCount=attack_amount
                    ))
        
        return actions
    
    @staticmethod
    def _late_game_strategy(
        player: Tower,
        enemies: List[Tower],
        resources: int,
        turn: int
    ) -> List[CombatAction]:
        """Late game strategy: Survive fatigue with strong defense, let fatigue kill opponents."""
        actions = []
        remaining = resources
        
        # Calculate fatigue damage
        fatigue_damage = FatigueCalculator.calculate_fatigue_damage(turn)
        next_fatigue = FatigueCalculator.calculate_fatigue_damage(turn + 1)
        
        # Priority 1: Build armor to survive fatigue
        # Build enough armor to survive next 2-3 turns of fatigue
        armor_needed = (fatigue_damage + next_fatigue) - player.armor
        if armor_needed > 0 and remaining >= armor_needed:
            armor_amount = min(armor_needed + 20, remaining)  # Extra buffer
            actions.append(ArmorAction(type="armor", amount=armor_amount))
            remaining -= armor_amount
        elif player.hp < 50 and remaining >= 30:
            # Build armor if HP is getting low
            armor_amount = min(50, remaining)
            actions.append(ArmorAction(type="armor", amount=armor_amount))
            remaining -= armor_amount
        
        # Priority 2: Light attacks only if we have excess resources
        if remaining >= 50:
            weakest = TargetSelector.find_weakest_tower(enemies)
            if weakest:
                # Only attack if opponent is very weak and we can eliminate them
                effective_hp = TargetSelector.calculate_effective_hp(weakest)
                if effective_hp < 50 and remaining >= effective_hp:
                    # Finish them off
                    actions.append(AttackAction(
                        type="attack",
                        targetId=weakest.playerId,
                        troopCount=effective_hp + 5
                    ))
                else:
                    # Light attack with 20% of remaining
                    attack_amount = int(remaining * 0.2)
                    if attack_amount > 0:
                        actions.append(AttackAction(
                            type="attack",
                            targetId=weakest.playerId,
                            troopCount=attack_amount
                        ))
        
        return actions
