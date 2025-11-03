# Built-in Bots Directory

This directory is for built-in bot implementations. Bots placed here will be automatically discovered and made available in the application.

## Bot Interface

All bots must implement the following interface:

```python
class MyPlayer:
    def __init__(self, my_color: int, opp_color: int):
        """
        Initialize the bot.
        
        Args:
            my_color: 0 for black, 1 for white
            opp_color: The opponent's color (0 or 1)
        """
        self.my_color = my_color
        self.opp_color = opp_color
    
    def select_move(self, board: list[list[int]]) -> tuple[int, int]:
        """
        Select a move given the current board state.
        
        Args:
            board: n×n 2D list where:
                   -1 = empty
                   0 = black
                   1 = white
        
        Returns:
            Tuple of (row, col) representing the selected move
        """
        # Your move selection logic here
        return (row, col)
```

## Adding a Built-in Bot

1. Create a new Python file in this directory (e.g., `my_bot.py`)
2. Implement a class following the interface above
3. Restart the backend server
4. The bot will appear in the available bots list

## Example

See `examples/random_player.py` in the repository root for a complete example.# Place your built-in bots here
