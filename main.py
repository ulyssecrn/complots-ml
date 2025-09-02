from game import Game
from cli_player import CLIPlayer
from ai_player import AIPlayer
from ai_strategies import BasicStrategy

def create_players(num_players: int, num_ai_players: int):
    """Create a mix of AI and human players."""
    if num_ai_players > num_players:
        raise ValueError("Number of AI players cannot exceed total players")
    
    players = []
    for i in range(num_players):
        if i < num_ai_players:
            players.append(AIPlayer(i, BasicStrategy()))
        else:
            players.append(CLIPlayer(i))
    return players

def main():
    # Initialize game
    while True:
        try:
            num_players = int(input("Enter number of players (3-6): "))
            if 3 <= num_players <= 6:
                break
            print("Number of players must be between 3 and 6")
        except ValueError:
            print("Please enter a valid number")
    
    while True:
        try:
            num_ai = int(input(f"Enter number of AI players (0-{num_players}): "))
            if 0 <= num_ai <= num_players:
                break
            print(f"Number of AI players must be between 0 and {num_players}")
        except ValueError:
            print("Please enter a valid number")
    
    # Create mix of AI and human players
    players = create_players(num_players, num_ai)
    
    # Pass player interfaces to game
    game = Game(num_players, players)
    game.deal_cards()
    
    # Main game loop
    while not game.is_game_over():
        current_player = players[game.current_player_idx]
        game_state = game.get_game_state()
        
        # Show game state before each turn
        CLIPlayer.print_game_state(game_state)
        
        # Print whose turn it is
        if isinstance(current_player, AIPlayer):
            print(f"\nAI Player {game.current_player_idx}'s turn...")
        
        # Get player's action
        valid_actions = game.get_valid_actions()
        action, target_id, claimed_role = current_player.choose_action(valid_actions, game_state)
        
        # Perform action
        success = game.perform_action(action, target_id, claimed_role)
        if not success:
            print("Action failed!")
        print("-" * 50)
    
    # Game over
    print("\nGame Over!")
    winners = [i for i, p in enumerate(game.players) if p.is_alive()]
    print(f"Winner(s): Player {winners[0]}")

if __name__ == "__main__":
    main()
