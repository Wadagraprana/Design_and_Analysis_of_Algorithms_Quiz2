# ==========================================
# GAME STATE MANAGEMENT
# ==========================================
import time


class GameState:
    """Manages the state of the game"""
    def __init__(self):
        self.started = False
        self.finished = False
        self.popup_open = False
        self.start_time = None
        self.end_time = None
        self.timer_reset = False
    
    def start_game(self) -> None:
        """Start the game"""
        self.started = True
        self.finished = False
        self.popup_open = False
        self.start_time = time.time()
        self.end_time = None
        self.timer_reset = False
    
    def end_game(self) -> None:
        """End the game"""
        self.started = False
        self.finished = True
        self.end_time = time.time()
    
    def reset_game(self) -> None:
        """Reset the game state"""
        self.started = False
        self.finished = False
        self.popup_open = False
        self.start_time = None
        self.end_time = None
        self.timer_reset = True
    
    def get_elapsed_time(self) -> float:
        """Get the elapsed time in seconds"""
        if self.timer_reset or (not self.started and not self.start_time):
            return 0
        elif self.start_time:
            return round((self.end_time if self.end_time else time.time()) - self.start_time, 1)
        else:
            return 0
