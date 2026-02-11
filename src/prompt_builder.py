"""Prompt builder for AI strategic decision-making."""
import json
from typing import List
from src.models import NegotiationRequest, CombatRequest, Tower
from src.fatigue import FatigueCalculator
from src.targeting import TargetSelector


class PromptBuilder:
    """Builds strategic prompts for AI models."""
    
    @staticmethod
    def build_negotiation_prompt(request: NegotiationRequest) -> str:
        """
        Build a prompt for negotiation phase decision-making.
        
        The prompt includes:
        - Game state (turn, towers, resources)
        - Strategic context (fatigue status, threats)
        - Instructions for alliance formation
        - Expected JSON response format
        """
        turn = request.turn
        player = request.playerTower
        enemies = request.enemyTowers
        
        # Calculate strategic context
        fatigue_active = FatigueCalculator.is_fatigue_active(turn)
        game_phase = FatigueCalculator.get_fatigue_phase(turn)
        
        # Filter alive enemies
        alive_enemies = TargetSelector.filter_alive_towers(enemies)
        
        # Find strongest threat
        strongest = TargetSelector.find_strongest_tower(alive_enemies)
        weakest = TargetSelector.find_weakest_tower(alive_enemies)
        
        prompt = f"""You are a strategic AI playing Kingdom Wars, a 4-player tower defense game. Your goal is to WIN by being the last tower standing.

CURRENT GAME STATE (Turn {turn}):

Your Tower:
- Player ID: {player.playerId}
- HP: {player.hp}
- Armor: {player.armor}
- Resources: {player.resources}
- Level: {player.level}
- Effective HP: {player.hp + player.armor}

Enemy Towers:
"""
        
        for enemy in alive_enemies:
            effective_hp = TargetSelector.calculate_effective_hp(enemy)
            prompt += f"""- Player {enemy.playerId}: HP={enemy.hp}, Armor={enemy.armor}, Level={enemy.level}, Effective HP={effective_hp}
"""
        
        prompt += f"""
GAME PHASE: {game_phase.upper()}
"""
        
        if fatigue_active:
            fatigue_damage = FatigueCalculator.calculate_fatigue_damage(turn)
            prompt += f"""FATIGUE ACTIVE: All towers take {fatigue_damage} damage this turn!
Fatigue doubles each turn: Turn {turn+1} will deal {fatigue_damage*2} damage.
"""
        else:
            turns_until = FatigueCalculator.turns_until_fatigue(turn)
            prompt += f"""Fatigue starts in {turns_until} turns (turn 25).
"""
        
        prompt += """
NEGOTIATION PHASE STRATEGY:

Your task is to form strategic alliances and declare attack intentions.

Key Principles:
1. Form alliances to eliminate the strongest threat
2. Coordinate attacks with allies
3. Never ally with someone who attacked you
4. In late game (fatigue), focus on eliminating weakest opponents quickly

ALLIANCE STRATEGY:
"""
        
        if strongest:
            prompt += f"""- Strongest threat: Player {strongest.playerId} (Level {strongest.level}, Effective HP {TargetSelector.calculate_effective_hp(strongest)})
- Consider allying with 2nd strongest to attack the leader
"""
        
        if weakest:
            prompt += f"""- Weakest target: Player {weakest.playerId} (Effective HP {TargetSelector.calculate_effective_hp(weakest)})
- In late game, coordinate to eliminate weak opponents
"""
        
        prompt += """
RESPONSE FORMAT:

Return a JSON array of diplomacy actions. Each action has:
- allyId: Player you won't attack (declare peace)
- attackTargetId: (Optional) Player you plan to attack

Example responses:
1. Form alliance and declare attack:
[{"allyId": 103, "attackTargetId": 102}]

2. Multiple alliances:
[{"allyId": 103, "attackTargetId": 102}, {"allyId": 104}]

3. No diplomacy:
[]

IMPORTANT RULES:
- Only one message per allyId
- Only include alive players
- Be strategic - alliances should help you win

Respond with ONLY the JSON array, no explanation:"""
        
        return prompt
    
    @staticmethod
    def build_combat_prompt(request: CombatRequest) -> str:
        """
        Build a prompt for combat phase decision-making.
        
        The prompt includes:
        - Complete game state
        - Strategic analysis (HP, threats, resources)
        - Phase-specific strategy guidance
        - Action costs and constraints
        - Expected JSON response format
        """
        turn = request.turn
        player = request.playerTower
        enemies = request.enemyTowers
        
        # Calculate strategic context
        fatigue_active = FatigueCalculator.is_fatigue_active(turn)
        game_phase = FatigueCalculator.get_fatigue_phase(turn)
        
        # Filter alive enemies
        alive_enemies = TargetSelector.filter_alive_towers(enemies)
        
        # Calculate costs
        from src.validators import ActionValidator
        upgrade_cost = ActionValidator.calculate_upgrade_cost(player.level)
        
        prompt = f"""You are a strategic AI playing Kingdom Wars. Your goal is to WIN by being the last tower standing.

CURRENT GAME STATE (Turn {turn}):

Your Tower:
- Player ID: {player.playerId}
- HP: {player.hp}
- Armor: {player.armor}
- Resources: {player.resources}
- Level: {player.level}
- Effective HP: {player.hp + player.armor}

Enemy Towers (ALIVE ONLY):
"""
        
        for enemy in alive_enemies:
            effective_hp = TargetSelector.calculate_effective_hp(enemy)
            status = "ALIVE" if enemy.hp > 0 else "DESTROYED"
            prompt += f"""- Player {enemy.playerId}: HP={enemy.hp}, Armor={enemy.armor}, Level={enemy.level}, Effective HP={effective_hp} [{status}]
"""
        
        prompt += f"""
GAME PHASE: {game_phase.upper()}
"""
        
        if fatigue_active:
            fatigue_damage = FatigueCalculator.calculate_fatigue_damage(turn)
            next_fatigue = FatigueCalculator.calculate_fatigue_damage(turn + 1)
            prompt += f"""
⚠️ FATIGUE ACTIVE ⚠️
- This turn: {fatigue_damage} damage to ALL towers
- Next turn: {next_fatigue} damage to ALL towers
- Fatigue DOUBLES each turn - game ending soon!
- Strategy: AGGRESSIVE ELIMINATION - attack to kill opponents before fatigue kills you
"""
        else:
            turns_until = FatigueCalculator.turns_until_fatigue(turn)
            prompt += f"""
Fatigue starts in {turns_until} turns (turn 25).
Strategy: Build resources, upgrade tower, eliminate weak opponents.
"""
        
        prompt += f"""
AVAILABLE ACTIONS:

1. Build Armor: {{"type": "armor", "amount": X}}
   - Cost: X × 1 resource
   - Blocks incoming damage
   - Only ONE armor action per turn
   - Use when HP is low or expecting heavy attacks

2. Attack: {{"type": "attack", "targetId": Y, "troopCount": Z}}
   - Cost: Z × 1 resource
   - Damages enemy armor first, then HP
   - Can attack multiple targets
   - ⚠️ NEVER attack destroyed towers (HP ≤ 0) - wastes resources!
   - No duplicate targetIds

3. Upgrade: {{"type": "upgrade"}}
   - Cost: {upgrade_cost} resources (Level {player.level}→{player.level+1})
   - Only ONE upgrade per turn
   - Increases resource generation per turn
   - Good investment in early/mid game

STRATEGIC GUIDANCE FOR {game_phase.upper()} GAME:
"""
        
        if game_phase == "early":
            prompt += """
EARLY GAME (Turns 1-10): RESOURCE GROWTH
- Priority: Upgrade to level 3-4 as fast as possible
- Build armor only if HP < 60
- Light attacks on weakest opponent to slow their growth
- Save resources for upgrades
"""
        elif game_phase == "mid":
            prompt += """
MID GAME (Turns 11-24): DOMINANCE
- Upgrade to level 4 if possible
- Focus attacks on weakest opponent until eliminated
- Build armor to maintain HP > 50
- Balance resource generation and attacks
"""
        else:  # late game
            prompt += """
LATE GAME (Turns 25+): SURVIVAL & ELIMINATION
- ⚠️ CRITICAL: Fatigue is active - aggressive strategy required!
- Spend 70-80% of resources on attacks
- Focus fire on single weakest opponent to eliminate them
- Minimal armor (only if HP < 30)
- NO UPGRADES - no time for ROI
- Goal: Eliminate all opponents before fatigue kills everyone
"""
        
        prompt += f"""
CRITICAL RULES:
1. ⚠️ NEVER attack towers with HP ≤ 0 (they're already destroyed!)
2. Total cost must not exceed {player.resources} resources
3. At most ONE armor action
4. At most ONE upgrade action
5. No duplicate attack targets

RESPONSE FORMAT:

Return a JSON array of actions. Examples:

1. Upgrade and attack:
[{{"type": "upgrade"}}, {{"type": "attack", "targetId": 102, "troopCount": 50}}]

2. Build armor and attack multiple targets:
[{{"type": "armor", "amount": 20}}, {{"type": "attack", "targetId": 102, "troopCount": 30}}, {{"type": "attack", "targetId": 103, "troopCount": 40}}]

3. All-in attack (late game):
[{{"type": "attack", "targetId": 102, "troopCount": {player.resources}}}]

4. No actions:
[]

Think strategically about:
- Your survival (HP + armor)
- Resource efficiency
- Eliminating threats
- Winning the game

Respond with ONLY the JSON array, no explanation:"""
        
        return prompt
