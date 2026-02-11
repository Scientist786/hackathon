"""Fatigue calculation logic for Kingdom Wars Bot."""


class FatigueCalculator:
    """Calculates fatigue damage and provides fatigue-related utilities."""
    
    FATIGUE_START_TURN = 25
    BASE_FATIGUE_DAMAGE = 10
    
    @staticmethod
    def calculate_fatigue_damage(turn: int) -> int:
        """
        Calculate fatigue damage for a given turn.
        
        Fatigue starts at turn 25.
        Damage formula: 10 × 2^(turn - 25)
        
        Turn 25: 10 damage
        Turn 26: 20 damage
        Turn 27: 40 damage
        Turn 28: 80 damage
        Turn 29: 160 damage
        Turn 30: 320 damage
        """
        if turn < FatigueCalculator.FATIGUE_START_TURN:
            return 0
        
        exponent = turn - FatigueCalculator.FATIGUE_START_TURN
        damage = FatigueCalculator.BASE_FATIGUE_DAMAGE * (2 ** exponent)
        return damage
    
    @staticmethod
    def is_fatigue_active(turn: int) -> bool:
        """Check if fatigue is currently active."""
        return turn >= FatigueCalculator.FATIGUE_START_TURN
    
    @staticmethod
    def turns_until_fatigue(turn: int) -> int:
        """Calculate how many turns until fatigue begins."""
        if turn >= FatigueCalculator.FATIGUE_START_TURN:
            return 0
        return FatigueCalculator.FATIGUE_START_TURN - turn
    
    @staticmethod
    def estimate_survival_turns(hp: int, armor: int, current_turn: int) -> int:
        """
        Estimate how many turns a tower can survive with given HP and armor.
        
        This assumes no additional armor is built and no healing occurs.
        Returns the number of additional turns the tower can survive.
        """
        if current_turn < FatigueCalculator.FATIGUE_START_TURN:
            # Before fatigue, survival is theoretically infinite
            # Return a large number to indicate pre-fatigue phase
            return 999
        
        effective_hp = hp + armor
        turns_survived = 0
        turn = current_turn
        
        while effective_hp > 0 and turns_survived < 20:  # Cap at 20 turns for safety
            turn += 1
            damage = FatigueCalculator.calculate_fatigue_damage(turn)
            effective_hp -= damage
            if effective_hp > 0:
                turns_survived += 1
        
        return turns_survived
    
    @staticmethod
    def get_fatigue_phase(turn: int) -> str:
        """
        Get the current game phase based on turn number.
        
        Returns:
            - "early": Turns 1-10 (resource growth phase)
            - "mid": Turns 11-24 (dominance phase)
            - "late": Turns 25+ (fatigue survival phase)
        """
        if turn <= 10:
            return "early"
        elif turn <= 24:
            return "mid"
        else:
            return "late"
