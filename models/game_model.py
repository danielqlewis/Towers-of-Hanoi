class GameModel:
    def __init__(self, disc_num: int = 3):
        self.towers = ([x for x in range(disc_num - 1, -1, -1)], [], [])
        self.reset_button_flag = False
        self.return_button_flag = False

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

    def toggle_reset_highlight(self) -> None:
        self.reset_button_flag = not self.reset_button_flag

    def toggle_return_highlight(self) -> None:
        self.return_button_flag = not self.return_button_flag
