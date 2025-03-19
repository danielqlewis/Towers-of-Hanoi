from enum import Enum
from collections import namedtuple

UserInput = namedtuple('UserInput', ['position', 'clicked'])


# Program state enumerations
class ProgramState(Enum):
    MENU = 0
    GAME = 1


class GameNotification(Enum):
    ILLEGAL_MOVE = 0
    VICTORY = 1


# Menu-related enumerations
class MenuState(Enum):
    MAIN = 0
    OPTIONS = 1
    TUTORIAL = 2
    CREDITS = 3


class MenuTheme(Enum):
    STANDARD = 0
    RED = 1
    BLUE = 2


class ButtonFlag(Enum):
    # Main menu buttons
    PLAY = 0
    OPTIONS = 1
    EXIT = 2
    TUTORIAL = 3
    CREDITS = 4

    # Options menu buttons
    DIFFICULTY_TOGGLE = 5
    RESOLUTION_TOGGLE = 6
    THEME_TOGGLE = 7
    BACK_TO_MAIN = 8
    ACCEPT_SETTINGS = 9

    # Game buttons
    RESET_BOARD = 10
