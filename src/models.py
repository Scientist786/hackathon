"""Data models for Kingdom Wars Bot."""
from pydantic import BaseModel, Field
from typing import List, Optional, Literal


class Tower(BaseModel):
    """Represents a player's tower in the game."""
    playerId: int = Field(..., description="Unique player identifier")
    hp: int = Field(..., ge=0, description="Health points")
    armor: int = Field(..., ge=0, description="Armor points")
    resources: int = Field(default=0, ge=0, description="Available resources")
    level: int = Field(..., ge=1, le=6, description="Tower level")


class CombatActionInfo(BaseModel):
    """Combat action information from previous turn."""
    targetId: int
    troopCount: int


class PreviousCombatAction(BaseModel):
    """Previous combat action by a player."""
    playerId: int
    action: CombatActionInfo


class DiplomacyActionInfo(BaseModel):
    """Diplomacy action information."""
    allyId: int
    attackTargetId: Optional[int] = None


class DiplomacyMessage(BaseModel):
    """Diplomacy message from a player."""
    playerId: int
    action: DiplomacyActionInfo


class NegotiationRequest(BaseModel):
    """Request payload for negotiation phase."""
    gameId: int
    turn: int = Field(..., ge=1)
    playerTower: Tower
    enemyTowers: List[Tower]
    combatActions: List[PreviousCombatAction] = Field(default_factory=list)


class CombatRequest(BaseModel):
    """Request payload for combat phase."""
    gameId: int
    turn: int = Field(..., ge=1)
    playerTower: Tower
    enemyTowers: List[Tower]
    diplomacy: List[DiplomacyMessage] = Field(default_factory=list)
    previousAttacks: List[PreviousCombatAction] = Field(default_factory=list)


# Response models
class DiplomacyAction(BaseModel):
    """Diplomacy action to send during negotiation."""
    allyId: int
    attackTargetId: Optional[int] = None


class ArmorAction(BaseModel):
    """Build armor action."""
    type: Literal["armor"] = "armor"
    amount: int = Field(..., gt=0)


class AttackAction(BaseModel):
    """Attack action."""
    type: Literal["attack"] = "attack"
    targetId: int
    troopCount: int = Field(..., gt=0)


class UpgradeAction(BaseModel):
    """Upgrade tower action."""
    type: Literal["upgrade"] = "upgrade"


# Union type for combat actions
CombatAction = ArmorAction | AttackAction | UpgradeAction


class BotInfo(BaseModel):
    """Bot metadata information."""
    name: str
    strategy: str
    version: str


class HealthCheck(BaseModel):
    """Health check response."""
    status: Literal["OK"] = "OK"
