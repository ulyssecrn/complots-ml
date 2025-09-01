from game import Game
from cli_player import CLIPlayer

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
    
    game = Game(num_players)
    game.deal_cards()
    
    # Create CLI players
    cli_players = [CLIPlayer(i) for i in range(num_players)]
    
    # Main game loop
    while not game.is_game_over():
        current_player = cli_players[game.current_player_idx]
        current_player.print_game_state(game)
        
        # Get player's action
        valid_actions = game.get_valid_actions()
        action, target_id, claimed_role = current_player.choose_action(valid_actions, game)
        
        # Perform action
        success = game.perform_action(action, target_id, claimed_role)
        if not success:
            print("Action failed!")
    
    # Game over
    print("\nGame Over!")
    winners = [i for i, p in enumerate(game.players) if p.is_alive()]
    print(f"Winner(s): Player {winners[0]}")

if __name__ == "__main__":
    main()
