from typing import List, Optional, Dict, Tuple
from game import Role, Action, RoleClaim, ActionResolution
from ai_strategies import AIStrategy, BasicStrategy

class AIPlayer:
    def __init__(self, player_id: int, strategy: AIStrategy = None):
        self.player_id = player_id
        self.strategy = strategy or BasicStrategy()  # Default to BasicStrategy if none provided
        self.action_history = []  # Track own actions
        
    def choose_action(self, valid_actions: List[Action], game_state) -> tuple[Action, Optional[int], Optional[Role]]:
        action, target_id, claimed_role = self.strategy.evaluate_action(game_state, valid_actions, self.player_id)
        self.action_history.append(action)
        print(f"AI Player {self.player_id} chooses action: {action.value} " +
              f"{'target: ' + str(target_id) if target_id else ''}")
        return action, target_id, claimed_role

    def wants_to_challenge(self, claim: RoleClaim, game_state) -> bool:
        should_challenge = self.strategy.should_challenge(claim, game_state, self.player_id)
        if should_challenge:
            print(f"AI Player {self.player_id} challenges Player {claim.player_id}'s {claim.role.value} claim")
        return should_challenge

    def wants_to_counter(self, resolution: ActionResolution, possible_roles: List[Role], game_state) -> Optional[Role]:
        counter_role = self.strategy.should_counter(resolution, possible_roles, game_state, self.player_id)
        if counter_role:
            print(f"AI Player {self.player_id} counters {resolution.action.value} with {counter_role.value}")
        return counter_role

    def choose_card_to_lose(self, cards) -> int:
        return self.strategy.choose_card_to_lose(cards, self.player_id)

    def choose_card_to_discard(self, cards) -> int:
        return self.strategy.choose_card_to_discard(cards, self.player_id)

    def wants_to_redo_spy(self, game_state) -> bool:
        decision = self.strategy.should_redo_spy(game_state, self.player_id)
        if decision:
            print(f"AI Player {self.player_id} redoes Spy action")
        return decision

    def chooses_pay_blackmail(self, game_state) -> bool:
        decision = self.strategy.should_pay_blackmail(game_state, self.player_id)
        print(f"AI Player {self.player_id} blackmail response: "
              f"{'pays 3 coins' if decision else 'loses a card'}")
        return decision

    def wants_to_claim_undertaker_coins(self, available_coins: int) -> bool:
        decision = self.strategy.should_claim_undertaker_coins(available_coins, self.player_id)
        if decision:
            print(f"AI Player {self.player_id} claims Undertaker for {available_coins} coins")
        return decision