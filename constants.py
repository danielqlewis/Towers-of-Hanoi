from enum import Enum


class ProgramState(Enum):
    MENU = 0
    GAME = 1


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
    PLAY = 0
    OPTIONS = 1
    EXIT = 2
    TUTORIAL = 3
    CREDITS = 4
    DIFFICULTY_TOGGLE = 5
    RESOLUTION_TOGGLE = 6
    THEME_TOGGLE = 7
    BACK_TO_MAIN = 8
    ACCEPT_SETTINGS = 9
    RESET_BOARD = 10
