# Complots ML

A Python implementation of the card game Coup, more specifically the variant Complots 2, a french sequel with novel roles.

## Description

This project implements a variation of the card game Coup where players have two face-down roles and can lie about their abilities. The game includes:
- 5 different roles (Illusionist, Spy, Undertaker, Pope, Blackmailer)
- Action challenging and countering mechanics
- CLI interface for human players

## How to Play

1. Run the game:
```bash
python main.py
```

2. Enter the number of players (2-6)

3. On your turn, you can:
- Take basic actions (Income, Foreign Aid)
- Use role-specific abilities
- Challenge other players' claims
- Counter certain actions

## Game Rules

### Roles
- **Illusionist**: Takes 4 coins, shares with other Illusionists
- **Spy**: Draws and exchanges cards, can pay to redo
- **Pope**: Takes 1 coin from each non-Pope player
- **Blackmailer**: Forces target to either give 3 coins or lose a card and receive 3 coins
- **Undertaker**: Counters Blackmailer

### Basic Actions
- **Income**: Take 1 coin
- **Foreign Aid**: Take 2 coins (can be blocked by Illusionist)
- **Coup**: Pay 7 coins to eliminate a card (mandatory at 10 coins)

## Development

This project is under development. Future additions will include:
- AI agent implementation
- Game statistics tracking