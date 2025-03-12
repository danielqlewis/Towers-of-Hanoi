from constants import ButtonFlag, GameNotification
from models.button_container import ButtonContainer


class GameModel:
    def __init__(self, disc_num: int = 3):
        self.towers = ([x for x in range(disc_num - 1, -1, -1)], [], [])
        button_list = [ButtonFlag.RESET_BOARD, ButtonFlag.BACK_TO_MAIN]
        self.active_buttons = ButtonContainer.create_buttons(button_list)
        self.highlighted_button = None
        self.selected_tower = None
        self.notification = None

    def check_move_legal(self, from_tower: int, to_tower: int) -> bool:
        if not self.towers[from_tower]:
            return False

        if not self.towers[to_tower]:
            return True

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

    def set_notification(self, new_notification: GameNotification):
        self.notification = new_notification

    def deset_notification(self):
        self.notification = None

    def set_highlight(self, new_highlight: ButtonFlag) -> None:
        self.highlighted_button = ButtonContainer(new_highlight)

    def deset_highlight(self) -> None:
        self.highlighted_button = None
