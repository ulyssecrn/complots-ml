import random

from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Dict

class Role(Enum):
    ILLUSIONIST = "Illusionist"
    SPY = "Spy"
    UNDERTAKER = "Undertaker"
    POPE = "Pope"
    BLACKMAILER = "Blackmailer"

class Card:
    def __init__(self, role: Role):
        self.role = role
        self.revealed = False

class Player:
    def __init__(self, name: str):
        self.name = name
        self.coins = 2
        self.cards = []
        
    def is_alive(self) -> bool:
        return any(not card.revealed for card in self.cards)

class Action(Enum):
    INCOME = "Income"           # Take 1 coin
    FOREIGN_AID = "Foreign Aid" # Take 2 coins
    COUP = "Coup"              # Pay 7 coins to eliminate a card
    # Role-specific actions
    ILLUSIONIST = "Illusionist"    # Take 4 coins, give 1 to other illusionists
    SPY = "Spy"                 # Take a card, choose to discard or exchange, can pay 1 to redo
    POPE = "Pope"     # Take 1 coin from each player who does not have the Pope
    BLACKMAILER = "Blackmailer"       # Take 3 coins from a player, or kill one role and pay 3, the other player decides

@dataclass
class RoleClaim:
    player_id: int
    role: Role
    is_counter: bool
    target_id: Optional[int] = None
    challenged_by: Optional[int] = None
    was_successful: bool = False

@dataclass
class ActionResolution:
    action: Action
    actor_id: int
    target_id: Optional[int]
    role_claims: List[RoleClaim] = None
    successful: bool = False

    def __post_init__(self):
        self.role_claims = self.role_claims or []

class Game:
    def __init__(self, num_players: int):
        self.players = [Player(f"Player_{i}") for i in range(num_players)]
        self.deck = self._initialize_deck()
        self.current_player_idx = 0
        self.action_stack = []  # Stack to track action resolution
        self.counters = {
            Action.FOREIGN_AID: [Role.ILLUSIONIST],
            Action.BLACKMAILER: [Role.UNDERTAKER],
            Action.POPE: [Role.POPE],
            Action.ILLUSIONIST: [Role.ILLUSIONIST]  # Add this line
        }
    
    def _initialize_deck(self) -> List[Card]:
        deck = []
        for role in Role:
            deck.extend([Card(role) for _ in range(3)])
        random.shuffle(deck)
        return deck
    
    def deal_cards(self):
        for player in self.players:
            player.cards = [self.deck.pop() for _ in range(2)]
    
    def get_valid_actions(self) -> List[Action]:
        """Returns list of valid actions for current player."""
        current_player = self.players[self.current_player_idx]
        valid_actions = [Action.INCOME, Action.FOREIGN_AID]
        
        # Coup is mandatory if player has 10 or more coins
        if current_player.coins >= 10:
            return [Action.COUP]
        
        # Add Coup if player has enough coins
        if current_player.coins >= 7:
            valid_actions.append(Action.COUP)
            
        # Add other actions based on coins
        if current_player.coins >= 3:
            valid_actions.append(Action.BLACKMAILER)
            
        # Add actions that don't require coins
        valid_actions.extend([
            Action.ILLUSIONIST,
            Action.SPY,
            Action.POPE
        ])
        
        return valid_actions

    def perform_action(self, action: Action, target_id: Optional[int] = None, claimed_role: Optional[Role] = None) -> bool:
        """Initiates an action and handles challenges/counters."""
        if action not in self.get_valid_actions():
            return False
            
        resolution = ActionResolution(
            action=action,
            actor_id=self.current_player_idx,
            target_id=target_id
        )

        # Add initial role claim if action requires a role
        if self._requires_role(action):
            if claimed_role is None:
                return False
            resolution.role_claims.append(RoleClaim(
                player_id=self.current_player_idx,
                role=claimed_role,
                is_counter=False,
                target_id=target_id
            ))

        # Handle counter phase
        if self._can_be_countered(action):
            self._handle_counters(resolution)

        # Handle challenge phase for all role claims
        self._handle_all_challenges(resolution)

        # Resolve all claims and execute action
        self._resolve_claims(resolution)
        if resolution.successful:
            self._execute_action(resolution)
        
        # Always advance to next turn, whether action succeeded or not
        self._next_turn()
        return resolution.successful

    def _requires_role(self, action: Action) -> bool:
        """Check if action requires a specific role."""
        return action in [Action.ILLUSIONIST, Action.SPY, Action.POPE, Action.BLACKMAILER]

    def _can_be_countered(self, action: Action) -> bool:
        """Check if action can be countered."""
        return action in self.counters

    def _handle_counters(self, resolution: ActionResolution) -> None:
        """Handle countering phase for an action."""
        possible_counter_roles = self.counters.get(resolution.action, [])
        
        # Special case for Blackmailer: only target can counter
        if resolution.action == Action.BLACKMAILER:
            if resolution.target_id is not None:
                counter_role = self._player_counters(resolution.target_id, resolution, possible_counter_roles)
                if counter_role:
                    resolution.role_claims.append(RoleClaim(
                        player_id=resolution.target_id,
                        role=counter_role,
                        is_counter=True
                    ))
            return

        # Normal counter handling for other actions
        for i, player in enumerate(self.players):
            if i != resolution.actor_id and player.is_alive():
                counter_role = self._player_counters(i, resolution, possible_counter_roles)
                if counter_role:
                    resolution.role_claims.append(RoleClaim(
                        player_id=i,
                        role=counter_role,
                        is_counter=True
                    ))

    def _handle_all_challenges(self, resolution: ActionResolution) -> None:
        """Handle challenges for all role claims."""
        for claim in resolution.role_claims:
            for i, player in enumerate(self.players):
                if i != claim.player_id and player.is_alive():
                    if self._player_challenges(i, claim):
                        claim.challenged_by = i
                        break

    def _resolve_claims(self, resolution: ActionResolution) -> None:
        """Resolve all claims and their challenges."""
        for claim in resolution.role_claims:
            if claim.challenged_by is not None:
                # Handle challenge
                has_role = self._player_has_role(claim.player_id, claim.role)
                if has_role:
                    # Challenge failed
                    self._eliminate_card(claim.challenged_by)
                    self._replace_card(claim.player_id, claim.role)
                    claim.was_successful = True
                else:
                    # Challenge succeeded
                    self._eliminate_card(claim.player_id, claim.role)
                    claim.was_successful = False
            else:
                # No challenge, claim succeeds
                claim.was_successful = True

        # Action succeeds if initial claim was successful
        initial_claim = next((claim for claim in resolution.role_claims 
                            if not claim.is_counter), None)
        if initial_claim:
            resolution.successful = initial_claim.was_successful
        else:
            resolution.successful = True

    def _execute_action(self, resolution: ActionResolution) -> None:
        """Execute the action based on successful claims."""
        current_player = self.players[resolution.actor_id]

        if resolution.action == Action.INCOME:
            current_player.coins += 1

        elif resolution.action == Action.FOREIGN_AID:
            # Check if any successful counters from illusionists
            if not any(claim.was_successful and claim.is_counter 
                      and claim.role == Role.ILLUSIONIST 
                      for claim in resolution.role_claims):
                current_player.coins += 2

        elif resolution.action == Action.ILLUSIONIST:
            # First check if action was successfully countered
            successful_counters = [claim for claim in resolution.role_claims 
                                if claim.is_counter and claim.was_successful]
            
            # Take 4 coins initially
            current_player.coins += 4
            
            # Get all successful illusionist claims (including counters)
            successful_illusionists = [claim.player_id for claim in resolution.role_claims 
                                     if claim.was_successful and claim.role == Role.ILLUSIONIST]
            
            # For each successful counter, give them 1 coin from the acting player
            for counter in successful_counters:
                if current_player.coins > 0:  # Check if actor still has coins
                    current_player.coins -= 1
                    self.players[counter.player_id].coins += 1
            
            # If there are 4 or fewer total illusionists (after counters), 
            # remaining coins are distributed to non-countering illusionists
            remaining_illusionists = [pid for pid in successful_illusionists 
                                    if pid != resolution.actor_id and
                                    pid not in [c.player_id for c in successful_counters]]
            
            if remaining_illusionists and len(successful_illusionists) <= 4:
                for player_id in remaining_illusionists:
                    if current_player.coins > 0:  # Check if actor still has coins
                        current_player.coins -= 1
                        self.players[player_id].coins += 1

        elif resolution.action == Action.BLACKMAILER:
            if resolution.target_id is None or current_player.coins < 3:
                return
            
            # Check if action was successfully countered
            if any(claim.was_successful and claim.is_counter 
                   and claim.role == Role.UNDERTAKER 
                   for claim in resolution.role_claims):
                return  # Action is blocked by successful Undertaker counter
            
            target_player = self.players[resolution.target_id]
            
            # If target has less than 3 coins, they must lose a card
            if target_player.coins < 3:
                # Let target choose which card to reveal
                self._eliminate_card(resolution.target_id)
                target_player.coins += 3
                current_player.coins -= 3
            else:
                # Target can choose to pay or lose a card
                if self._player_chooses_pay_blackmail(resolution.target_id):
                    # Target pays 3 coins
                    target_player.coins -= 3
                    current_player.coins += 3
                else:
                    # Target loses a card but gets 3 coins
                    self._eliminate_card(resolution.target_id)
                    target_player.coins += 3
                    current_player.coins -= 3

        elif resolution.action == Action.SPY:
            # Draw new card
            new_card = self.deck.pop()
            current_player.cards.append(new_card)
            
            # Let player choose which card to discard
            card_index = self._player_choose_card_to_discard(resolution.actor_id)
            discarded_card = current_player.cards.pop(card_index)
            self.deck.append(discarded_card)
            random.shuffle(self.deck)
            
            # Option to redo for 1 coin
            while current_player.coins >= 1 and self._player_wants_redo_spy(resolution.actor_id):
                current_player.coins -= 1
                # Draw new card again
                new_card = self.deck.pop()
                current_player.cards.append(new_card)
                # Choose which to discard again
                card_index = self._player_choose_card_to_discard(resolution.actor_id)
                discarded_card = current_player.cards.pop(card_index)
                self.deck.append(discarded_card)
                random.shuffle(self.deck)

        elif resolution.action == Action.POPE:
            # Example of partial success based on counters
            for i, player in enumerate(self.players):
                if i != resolution.actor_id:
                    # Check if this player successfully countered
                    was_countered = any(claim.player_id == i 
                                      and claim.was_successful 
                                      and claim.is_counter 
                                      for claim in resolution.role_claims)
                    if not was_countered:
                        # Take coin from player
                        if player.coins > 0:
                            player.coins -= 1
                            self.players[resolution.actor_id].coins += 1


    def _replace_card(self, player_id: int, role: Role) -> None:
        """Replace a shown card with a new one from the deck."""
        player = self.players[player_id]
        for i, card in enumerate(player.cards):
            if card.role == role:
                player.cards[i] = self.deck.pop()
                self.deck.append(card)
                random.shuffle(self.deck)
                break

    def _eliminate_card(self, player_id: int) -> None:
        """Let a player choose one of their cards to reveal when losing a challenge."""
        player = self.players[player_id]
        available_cards = [i for i, card in enumerate(player.cards) if not card.revealed]
        if available_cards:
            # Let player choose which card to reveal
            card_index = self._player_choose_card_to_lose(player_id)
            player.cards[card_index].revealed = True

    def _player_challenges(self, player_id: int, claim: RoleClaim) -> bool:
        from cli_player import CLIPlayer
        cli_player = CLIPlayer(player_id)
        return cli_player.wants_to_challenge(claim, self)

    def _player_counters(self, player_id: int, resolution: ActionResolution, possible_roles: List[Role]) -> Optional[Role]:
        from cli_player import CLIPlayer
        cli_player = CLIPlayer(player_id)
        return cli_player.wants_to_counter(resolution, possible_roles, self)

    def _player_choose_card_to_discard(self, player_id: int) -> int:
        from cli_player import CLIPlayer
        cli_player = CLIPlayer(player_id)
        return cli_player.choose_card_to_discard(self.players[player_id].cards)

    def _player_wants_redo_spy(self, player_id: int) -> bool:
        from cli_player import CLIPlayer
        cli_player = CLIPlayer(player_id)
        return cli_player.wants_to_redo_spy()

    def _player_chooses_pay_blackmail(self, player_id: int) -> bool:
        from cli_player import CLIPlayer
        cli_player = CLIPlayer(player_id)
        return cli_player.chooses_pay_blackmail()

    def is_game_over(self) -> bool:
        """Returns True if only one player remains alive."""
        alive_players = sum(1 for player in self.players if player.is_alive())
        return alive_players <= 1

    def _next_turn(self) -> None:
        """Advances to the next player's turn."""
        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
        # Skip dead players
        while not self.players[self.current_player_idx].is_alive():
            self.current_player_idx = (self.current_player_idx + 1) % len(self.players)

    def _player_has_role(self, player_id: int, role: Role) -> bool:
        """Check if player has the claimed role in their non-revealed cards."""
        player = self.players[player_id]
        return any(card.role == role and not card.revealed 
                  for card in player.cards)
    
    def _player_choose_card_to_lose(self, player_id: int) -> int:
        """Ask player which card they want to reveal when losing a challenge/card."""
        from cli_player import CLIPlayer
        cli_player = CLIPlayer(player_id)
        return cli_player.choose_card_to_lose(self.players[player_id].cards)