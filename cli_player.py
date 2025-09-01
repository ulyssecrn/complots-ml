from typing import List, Optional
from game import Role, Action, RoleClaim, ActionResolution

class CLIPlayer:
    def __init__(self, player_id: int):
        self.player_id = player_id

    def choose_action(self, valid_actions: List[Action], game_state) -> tuple[Action, Optional[int], Optional[Role]]:
        """Ask player to choose an action and its parameters."""
        print("\nYour turn! Choose an action:")
        for i, action in enumerate(valid_actions):
            print(f"{i}: {action.value}")
        
        while True:
            try:
                choice = int(input("Enter action number: "))
                if 0 <= choice < len(valid_actions):
                    action = valid_actions[choice]
                    target_id = None
                    claimed_role = None

                    # Get target if needed
                    if action in [Action.BLACKMAILER, Action.COUP]:
                        print("\nChoose target player:")
                        for i, player in enumerate(game_state.players):
                            if i != self.player_id and player.is_alive():
                                print(f"{i}: Player {i} (coins: {player.coins})")
                        target_id = int(input("Enter target player number: "))

                    # Get claimed role if needed
                    if action in [Action.ILLUSIONIST, Action.SPY, Action.POPE, Action.BLACKMAILER]:
                        claimed_role = Role[action.name]

                    return action, target_id, claimed_role
            except (ValueError, IndexError):
                print("Invalid choice, try again")

    def wants_to_challenge(self, claim: RoleClaim, game_state) -> bool:
        """Ask player if they want to challenge a claim."""
        print(f"\n=== Challenge Phase ===")
        print(f"Player {claim.player_id} claims to be {claim.role.value}")
        if claim.is_counter:
            print(f"This is a counter to the original action.")
        response = input(f"Player {self.player_id}, do you want to challenge? (y/n): ").lower() == 'y'
        if response:
            print("Challenge initiated! Resolving...")
        return response

    def announce_challenge_result(self, challenger_id: int, challenged_id: int, role: Role, was_successful: bool):
        """Display the result of a challenge."""
        print("\n=== Challenge Result ===")
        if was_successful:
            print(f"Player {challenged_id} was LYING about having {role.value}!")
            print(f"They lose their claimed card.")
        else:
            print(f"Player {challenged_id} HAD the {role.value}!")
            print(f"Player {challenger_id} loses a card.")
        print("======================")

    def wants_to_counter(self, resolution: ActionResolution, possible_roles: List[Role], game_state) -> Optional[Role]:
        """Ask player if they want to counter an action."""
        print(f"\n=== Counter Phase ===")
        print(f"Player {resolution.actor_id} is attempting {resolution.action.value}")
        print(f"You can counter this with: {[role.value for role in possible_roles]}")
        if input(f"Player {self.player_id}, do you want to counter? (y/n): ").lower() == 'y':
            return possible_roles[0]
        return None

    def choose_card_to_discard(self, cards) -> int:
        """Ask player which card they want to discard."""
        print("\nYour cards:")
        for i, card in enumerate(cards):
            print(f"{i}: {card.role.value}")
        while True:
            try:
                choice = int(input("Choose card to discard: "))
                if 0 <= choice < len(cards):
                    return choice
            except ValueError:
                pass
            print("Invalid choice, try again")

    def wants_to_redo_spy(self) -> bool:
        """Ask if player wants to redo spy action."""
        return input("Do you want to pay 1 coin to redo the spy action? (y/n): ").lower() == 'y'

    def chooses_pay_blackmail(self) -> bool:
        """Ask player if they want to pay the blackmail or lose a card."""
        print("\nYou are being blackmailed!")
        print("1: Pay 3 coins")
        print("2: Lose a card and receive 3 coins")
        while True:
            choice = input("What's your choice? (1/2): ")
            if choice in ['1', '2']:
                return choice == '1'
            print("Invalid choice, try again")

    @staticmethod
    def print_game_state(game_state):
        """Display the current game state."""
        print("\n=== Game State ===")
        print(f"Current Turn: Player {game_state.current_player_idx}")
        print("-------------------")
        for i, player in enumerate(game_state.players):
            # Count alive and dead cards
            alive_cards = [card.role.value for card in player.cards if not card.revealed]
            dead_cards = [f"{card.role.value}(revealed)" for card in player.cards if card.revealed]
            
            status = "🟢 ALIVE" if player.is_alive() else "💀 DEAD"
            cards_str = f"Alive cards: [{', '.join(alive_cards)}]"
            if dead_cards:
                cards_str += f", Dead cards: [{', '.join(dead_cards)}]"
            
            # Add arrow indicator for current player
            player_indicator = "➤ " if i == game_state.current_player_idx else "  "
            print(f"{player_indicator}Player {i}: {status}")
            print(f"  Coins: {player.coins}")
            print(f"  {cards_str}")
        print("================")

    def choose_card_to_lose(self, cards) -> int:
        """Ask player which card they want to reveal."""
        print("\nChoose a card to reveal:")
        available_cards = [(i, card) for i, card in enumerate(cards) if not card.revealed]
        for i, card in available_cards:
            print(f"{i}: {card.role.value}")
        while True:
            try:
                choice = int(input("Choose card to reveal: "))
                if any(i == choice for i, _ in available_cards):
                    return choice
            except ValueError:
                pass
            print("Invalid choice, try again")