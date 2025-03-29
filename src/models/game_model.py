from src.constants import ButtonFlag, GameNotification
from src.models.button_entity import ButtonEntity
from typing import Optional


class GameModel:
    """
    Manages the game board state and game logic for Towers of Hanoi.

    This class maintains the state of the three towers and discs, implements
    game rules including move validation, and tracks game state such as
    selected towers and notifications.

    Attributes:
        towers: A tuple of three lists representing the towers and their discs.
        active_buttons: A list of ButtonEntity objects for game interface.
        highlighted_button: Currently highlighted button or None.
        selected_tower: Index of currently selected tower or None.
        notification: Current game notification message or None.
    """

    def __init__(self, disc_num: int = 3):
        """
        Initialize a new game with the specified number of discs.

        Discs are represented as integers, with smaller numbers representing
        larger discs. All discs are initially placed on the first tower in
        descending order (largest to smallest).

        Args:
            disc_num: Number of discs to use in the game. Default is 3.
        """
        self.towers = ([x for x in range(disc_num - 1, -1, -1)], [], [])
        button_list = [ButtonFlag.RESET_BOARD, ButtonFlag.BACK_TO_MAIN]
        self.active_buttons = ButtonEntity.create_buttons(button_list)
        self.highlighted_button = None
        self.selected_tower = None
        self.notification = None

    def check_move_legal(self, from_tower: int, to_tower: int) -> bool:
        """
        Determine if moving a disc between towers is a legal move.

        Enforces the fundamental rule of Towers of Hanoi: a larger disc
        cannot be placed on a smaller one. Also checks if the source
        tower has any discs to move.

        Args:
            from_tower: Index of the source tower (0, 1, or 2).
            to_tower: Index of the destination tower (0, 1, or 2).

        Returns:
            True if the move is legal, False otherwise.
        """
        if not self.towers[from_tower]:
            return False

        if not self.towers[to_tower]:
            return True

        return self.towers[from_tower][-1] < self.towers[to_tower][-1]

    def move_disc(self, from_tower: int, to_tower: int) -> None:
        """
        Move a disc from one tower to another.

        Takes the top disc from the source tower and places it on top
        of the destination tower. This method assumes the move has already
        been validated as legal.

        Args:
            from_tower: Index of the source tower (0, 1, or 2).
            to_tower: Index of the destination tower (0, 1, or 2).
        """
        moved_disc = self.towers[from_tower].pop()
        self.towers[to_tower].append(moved_disc)

    def is_complete(self) -> bool:
        """
        Check if the puzzle has been solved.

        The puzzle is complete when all discs have been moved to the third tower
        (index 2), meaning the first two towers are empty.

        Returns:
            True if the puzzle is solved, False otherwise.
        """
        if self.towers[0] or self.towers[1]:
            return False
        return True

    def reset_board(self) -> None:
        """
        Reset the game board to its initial state.

        Clears the tower selection and moves all discs back to the first tower
        in the proper order (largest to smallest).
        """
        self.selected_tower = None
        disc_num = sum([len(x) for x in self.towers])
        self.towers = ([x for x in range(disc_num - 1, -1, -1)], [], [])

    def set_selected_tower(self, tower: Optional[int]) -> None:
        """
        Set or clear the currently selected tower.

        Args:
            tower: Index of the tower to select (0, 1, or 2), or None to deselect.
        """
        self.selected_tower = tower

    def set_notification(self, new_notification: GameNotification) -> None:
        """
        Set a notification message to be displayed in the game.

        Args:
            new_notification: GameNotification enum value representing the
                notification to display.
        """
        self.notification = new_notification

    def clear_notification(self) -> None:
        """
        Clear the current notification message.
        """
        self.notification = None

    def set_highlight(self, new_highlight: ButtonFlag) -> None:
        """
        Highlight a specific button in the game interface.

        Args:
            new_highlight: ButtonFlag enum value identifying the button to highlight.
        """
        self.highlighted_button = ButtonEntity(new_highlight)

    def clear_highlight(self) -> None:
        """
        Clear any button highlighting.
        """
        self.highlighted_button = None
