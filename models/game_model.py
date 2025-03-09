from pygame import Rect
from constants import ButtonFlag

BUTTON_LOCATIONS = {ButtonFlag.RESET_BOARD: (900, 60),
                    ButtonFlag.BACK_TO_MAIN: (60, 60)}

BUTTON_SIZE = (75, 75)


class ButtonContainer:
    def __init__(self, flag, location):
        self.flag = flag
        self.rect = Rect(0, 0, *BUTTON_SIZE)
        self.rect.center = location


class GameModel:
    def __init__(self, disc_num: int = 3):
        self.towers = ([x for x in range(disc_num - 1, -1, -1)], [], [])
        button_list = [ButtonFlag.RESET_BOARD, ButtonFlag.BACK_TO_MAIN]
        self.active_buttons = [ButtonContainer(x, BUTTON_LOCATIONS[x]) for x in button_list]
        self.highlighed_button = None

    def check_move_legal(self, from_tower: int, to_tower: int) -> bool:
        if not self.towers[to_tower]:
            return True
        elif not self.towers[from_tower]:
            return False
        else:
            return self.towers[from_tower][-1] < self.towers[to_tower][-1]

    def move_disc(self, from_tower: int, to_tower: int) -> None:
        moved_disc = self.towers[from_tower].pop()
        self.towers[to_tower].append(moved_disc)

    def is_complete(self) -> bool:
        if self.towers[0] or self.towers[1]:
            return False
        return True

    def reset_board(self) -> None:
        disc_num = sum([len(x) for x in self.towers])
        self.towers = ([x for x in range(disc_num - 1, -1, -1)], [], [])

    def set_highlight(self, new_highlight: ButtonFlag) -> None:
        self.highlighed_button = new_highlight

    def deset_highlight(self) -> None:
        self.highlighed_button = None
