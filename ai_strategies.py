from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Dict
from game import Action, Role, RoleClaim, ActionResolution

class AIStrategy(ABC):
    @abstractmethod
    def evaluate_action(self, game_state, valid_actions: List[Action], player_id: int) -> tuple[Action, Optional[int], Optional[Role]]:
        """Choose and evaluate an action to perform."""
        pass
    
    @abstractmethod
    def should_challenge(self, claim: RoleClaim, game_state, player_id: int) -> bool:
        """Decide whether to challenge a claim."""
        pass
    
    @abstractmethod
    def should_counter(self, resolution: ActionResolution, possible_roles: List[Role], game_state, player_id: int) -> Optional[Role]:
        """Decide whether to counter an action."""
        pass
    
    @abstractmethod
    def choose_card_to_lose(self, cards: List[Role], player_id: int) -> int:
        """Choose which card to reveal when losing one."""
        pass
    
    @abstractmethod
    def choose_card_to_discard(self, cards: List[Role], player_id: int) -> int:
        """Choose which card to discard for Spy action."""
        pass
    
    @abstractmethod
    def should_redo_spy(self, game_state, player_id: int) -> bool:
        """Decide whether to pay to redo Spy action."""
        pass
    
    @abstractmethod
    def should_pay_blackmail(self, game_state, player_id: int) -> bool:
        """Decide whether to pay when blackmailed."""
        pass
    
    @abstractmethod
    def should_claim_undertaker_coins(self, available_coins: int, game_state, player_id: int) -> bool:
        """Decide whether to claim Undertaker for coins."""
        pass

class BasicStrategy(AIStrategy):
    """Basic strategy that:
    1. Always coups at 7+ coins the player with most coins
    2. Chooses Income otherwise
    3. Never challenges or counters
    4. Always pays blackmail
    5. Never claims Undertaker
    """
    def evaluate_action(self, game_state, valid_actions: List[Action], player_id: int) -> tuple[Action, Optional[int], Optional[Role]]:
        current_player = game_state.players[player_id]
            
        # Prefer coup if we can afford it
        if current_player.coins >= 7 and Action.COUP in valid_actions:
            target_id = self._choose_coup_target(game_state, player_id)
            return Action.COUP, target_id, None
            
        # Take income otherwise
        return Action.INCOME, None, None
    
    def should_challenge(self, claim: RoleClaim, game_state, player_id: int) -> bool:
        return False
    
    def should_counter(self, resolution: ActionResolution, possible_roles: List[Role], game_state, player_id: int) -> Optional[Role]:
        return None
    
    def choose_card_to_lose(self, cards: List[Role], player_id: int) -> int:
        # Choose first available card
        return next((i for i, card in enumerate(cards) if not card.revealed), 0)
    
    def choose_card_to_discard(self, cards: List[Role], player_id: int) -> int:
        return 0
    
    def should_redo_spy(self, game_state, player_id: int) -> bool:
        return False
    
    def should_pay_blackmail(self, game_state, player_id: int) -> bool:
        return True

    def should_claim_undertaker_coins(self, available_coins: int, game_state, player_id: int) -> bool:
        return False
        
    def _choose_coup_target(self, game_state, player_id: int) -> Optional[int]:
        max_coins = -1
        target_id = None
        for i, player in enumerate(game_state.players):
            if i != player_id and player.is_alive() and player.coins > max_coins:
                max_coins = player.coins
                target_id = i
        return target_id
