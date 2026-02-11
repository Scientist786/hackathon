"""Core strategy engine with AI-powered decision making."""
import json
import logging
from typing import List, Optional
from src.models import (
    NegotiationRequest, CombatRequest, DiplomacyAction, CombatAction
)
from src.bedrock_client import BedrockClient
from src.prompt_builder import PromptBuilder
from src.fallback_strategy import FallbackStrategy
from src.validators import ActionValidator
from src.targeting import TargetSelector

logger = logging.getLogger(__name__)


class StrategyEngine:
    """Core decision-making engine using AI and fallback strategies."""
    
    def __init__(self, bedrock_client: Optional[BedrockClient] = None):
        """
        Initialize strategy engine.
        
        Args:
            bedrock_client: AWS Bedrock client for AI inference (optional)
        """
        self.bedrock_client = bedrock_client
        self.fallback_strategy = FallbackStrategy()
    
    async def decide_negotiation(self, request: NegotiationRequest) -> List[DiplomacyAction]:
        """
        Decide negotiation actions using AI or fallback strategy.
        
        Process:
        1. Build strategic prompt
        2. Call AI model
        3. Parse and validate response
        4. Fall back to heuristics if AI fails
        
        Returns:
            List of diplomacy actions
        """
        logger.info(f"Deciding negotiation for turn {request.turn}")
        
        # Try AI-powered decision
        if self.bedrock_client:
            try:
                prompt = PromptBuilder.build_negotiation_prompt(request)
                logger.debug(f"Negotiation prompt: {prompt[:200]}...")
                
                response = self.bedrock_client.invoke_model_with_retry(prompt)
                
                if response:
                    actions = self._parse_diplomacy_response(response, request)
                    if actions is not None:
                        logger.info(f"AI generated {len(actions)} diplomacy actions")
                        return actions
                
                logger.warning("AI failed to generate valid negotiation actions")
            except Exception as e:
                logger.error(f"Error in AI negotiation: {e}")
        
        # Fall back to rule-based strategy
        logger.info("Using fallback negotiation strategy")
        return self.fallback_strategy.generate_negotiation_actions(request)
    
    async def decide_combat(self, request: CombatRequest) -> List[CombatAction]:
        """
        Decide combat actions using AI or fallback strategy.
        
        Process:
        1. Build strategic prompt with game state
        2. Call AI model
        3. Parse and validate response
        4. Validate actions against game rules
        5. Filter out attacks on destroyed towers
        6. Fall back to heuristics if AI fails or actions invalid
        
        Returns:
            List of combat actions
        """
        logger.info(f"Deciding combat for turn {request.turn}")
        
        # Try AI-powered decision
        if self.bedrock_client:
            try:
                prompt = PromptBuilder.build_combat_prompt(request)
                logger.debug(f"Combat prompt: {prompt[:200]}...")
                
                response = self.bedrock_client.invoke_model_with_retry(prompt)
                
                if response:
                    actions = self._parse_combat_response(response, request)
                    if actions is not None:
                        # Validate actions
                        validation = ActionValidator.validate_combat_actions(
                            actions,
                            request.playerTower.resources,
                            request.playerTower.level
                        )
                        
                        if validation.valid:
                            # Filter out attacks on destroyed towers
                            filtered_actions = self._filter_invalid_attacks(actions, request.enemyTowers)
                            logger.info(f"AI generated {len(filtered_actions)} valid combat actions")
                            return filtered_actions
                        else:
                            logger.warning(f"AI actions invalid: {validation.errors}")
                
                logger.warning("AI failed to generate valid combat actions")
            except Exception as e:
                logger.error(f"Error in AI combat: {e}")
        
        # Fall back to rule-based strategy
        logger.info("Using fallback combat strategy")
        return self.fallback_strategy.generate_combat_actions(request)
    
    def _parse_diplomacy_response(
        self,
        response: str,
        request: NegotiationRequest
    ) -> Optional[List[DiplomacyAction]]:
        """
        Parse AI response into diplomacy actions.
        
        Validates:
        - Valid JSON array
        - No duplicate allyIds
        - Only alive players referenced
        
        Returns:
            List of diplomacy actions, or None if parsing fails
        """
        try:
            # Extract JSON from response (may have extra text)
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            
            if json_start == -1 or json_end == 0:
                logger.warning("No JSON array found in AI response")
                return None
            
            json_str = response[json_start:json_end]
            data = json.loads(json_str)
            
            if not isinstance(data, list):
                logger.warning("AI response is not a list")
                return None
            
            # Parse into DiplomacyAction objects
            actions = []
            seen_ally_ids = set()
            alive_enemy_ids = {tower.playerId for tower in request.enemyTowers if tower.hp > 0}
            
            for item in data:
                if not isinstance(item, dict):
                    continue
                
                ally_id = item.get('allyId')
                if not ally_id or ally_id in seen_ally_ids:
                    continue  # Skip invalid or duplicate
                
                # Verify ally is alive
                if ally_id not in alive_enemy_ids:
                    logger.warning(f"Ally {ally_id} is not alive, skipping")
                    continue
                
                seen_ally_ids.add(ally_id)
                
                attack_target_id = item.get('attackTargetId')
                # Verify attack target is alive if specified
                if attack_target_id and attack_target_id not in alive_enemy_ids:
                    logger.warning(f"Attack target {attack_target_id} is not alive, removing")
                    attack_target_id = None
                
                actions.append(DiplomacyAction(
                    allyId=ally_id,
                    attackTargetId=attack_target_id
                ))
            
            return actions
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI diplomacy response as JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"Error parsing diplomacy response: {e}")
            return None
    
    def _parse_combat_response(
        self,
        response: str,
        request: CombatRequest
    ) -> Optional[List[CombatAction]]:
        """
        Parse AI response into combat actions.
        
        Returns:
            List of combat actions, or None if parsing fails
        """
        try:
            # Extract JSON from response
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            
            if json_start == -1 or json_end == 0:
                logger.warning("No JSON array found in AI response")
                return None
            
            json_str = response[json_start:json_end]
            data = json.loads(json_str)
            
            if not isinstance(data, list):
                logger.warning("AI response is not a list")
                return None
            
            # Parse into CombatAction objects
            actions = []
            
            for item in data:
                if not isinstance(item, dict):
                    continue
                
                action_type = item.get('type')
                
                if action_type == 'armor':
                    amount = item.get('amount')
                    if amount and amount > 0:
                        from src.models import ArmorAction
                        actions.append(ArmorAction(type='armor', amount=amount))
                
                elif action_type == 'attack':
                    target_id = item.get('targetId')
                    troop_count = item.get('troopCount')
                    if target_id and troop_count and troop_count > 0:
                        from src.models import AttackAction
                        actions.append(AttackAction(
                            type='attack',
                            targetId=target_id,
                            troopCount=troop_count
                        ))
                
                elif action_type == 'upgrade':
                    from src.models import UpgradeAction
                    actions.append(UpgradeAction(type='upgrade'))
            
            return actions
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI combat response as JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"Error parsing combat response: {e}")
            return None
    
    def _filter_invalid_attacks(
        self,
        actions: List[CombatAction],
        enemies: List
    ) -> List[CombatAction]:
        """
        Filter out attacks on destroyed towers (HP ≤ 0).
        
        This is CRITICAL - attacking destroyed towers wastes resources.
        """
        from src.models import AttackAction
        
        alive_enemy_ids = {tower.playerId for tower in enemies if tower.hp > 0}
        
        filtered = []
        for action in actions:
            if isinstance(action, AttackAction):
                if action.targetId in alive_enemy_ids:
                    filtered.append(action)
                else:
                    logger.warning(f"Filtered out attack on destroyed tower {action.targetId}")
            else:
                filtered.append(action)
        
        return filtered
