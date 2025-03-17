from pygame import Rect
from src.constants import ButtonFlag
from typing import Tuple, Dict, List


BUTTON_POSITIONS: Dict[ButtonFlag, Tuple[int, int]] = {
    # Main menu buttons
    ButtonFlag.PLAY: (480, 300),
    ButtonFlag.OPTIONS: (480, 400),
    ButtonFlag.EXIT: (480, 500),
    ButtonFlag.TUTORIAL: (140, 570),
    ButtonFlag.CREDITS: (820, 570),

    # Options menu buttons
    ButtonFlag.DIFFICULTY_TOGGLE: (400, 220),
    ButtonFlag.RESOLUTION_TOGGLE: (400, 340),
    ButtonFlag.THEME_TOGGLE: (400, 460),
    ButtonFlag.ACCEPT_SETTINGS: (480, 560),

    # Game buttons
    ButtonFlag.RESET_BOARD: (900, 60),
    ButtonFlag.BACK_TO_MAIN: (60, 60)
}

STANDARD_BUTTON_SIZE: Tuple[int, int] = (200, 80)
SMALL_BUTTON_SIZE: Tuple[int, int] = (75, 75)


class ButtonContainer:
    """
    Represents a clickable button in the game.

    Attributes:
        flag (ButtonFlag): The type of button
        rect (Rect): The button's collision rectangle
    """

    def __init__(self, flag: ButtonFlag):
        self.flag = flag

        # Determine button size based on type
        if flag in (ButtonFlag.BACK_TO_MAIN, ButtonFlag.RESET_BOARD):
            button_size = SMALL_BUTTON_SIZE
        else:
            button_size = STANDARD_BUTTON_SIZE

        # Create button rectangle
        self.rect = Rect(0, 0, *button_size)

        # look up predefined position
        if flag in BUTTON_POSITIONS:
            position = BUTTON_POSITIONS[flag]
        else:
            raise ValueError(f"No predefined position for button {flag}")

        # Center the rectangle at the position
        self.rect.center = position

    @classmethod
    def create_buttons(cls, button_flags: List[ButtonFlag]) -> List["ButtonContainer"]:
        return [cls(flag) for flag in button_flags]