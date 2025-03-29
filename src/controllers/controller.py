from src.constants import ProgramState, ButtonFlag, MenuState, GameNotification, UserInput
from src.models.menu_model import MenuModel
from src.models.game_model import GameModel
from typing import Tuple, Union, Optional


class ProgramController:
    """
    Processes user input and updates the appropriate model.

    This class serves as the intermediary between user input and model state changes,
    handling button interactions, tower selections, game moves, and state transitions.

    Attributes:
        model: The currently active model (menu or game).
        model_updated: Flag indicating if the model has changed and needs rerendering.
        next_state: Requested transition between menu and game states.
        exit_flag: Flag indicating the program should terminate.
        asset_package_updated: Flag indicating the visual theme has changed.
        resolution_updated: Flag indicating the screen resolution has changed.
        LEFT_TOWER_BOUNDARY: X-coordinate separating left and middle towers.
        RIGHT_TOWER_BOUNDARY: X-coordinate separating middle and right towers.
    """
    # Tower boundary constants
    LEFT_TOWER_BOUNDARY = 320
    RIGHT_TOWER_BOUNDARY = 640

    def __init__(self, model: MenuModel):
        """
        Initialize a new controller with the menu model.

        Args:
            model: The initial MenuModel to control.
        """
        self.model = model
        self.model_updated = False
        self.next_state: Optional[ProgramState] = None
        self.exit_flag = False
        self.asset_package_updated = False
        self.resolution_updated = False

    def reset_settings_update_flags(self) -> None:
        """
        Reset flags that indicate settings have changed.

        Called after the ProgramLoop has handled theme and resolution changes.
        """
        self.asset_package_updated = False
        self.resolution_updated = False

    def reset_render_flag(self) -> None:
        """
        Reset the flag that indicates the model needs rerendering.

        Called after the ProgramLoop has rerendered the screen.
        """
        self.model_updated = False

    def update_state(self, new_model: Union[MenuModel, GameModel]) -> None:
        """
        Update the controller with a new active model.

        Called during state transitions between menu and game.

        Args:
            new_model: The new model (menu or game) to control.
        """
        self.model = new_model
        self.next_state = None
        self.model_updated = True

    def _should_update_highlight(self, program_state: ProgramState) -> bool:
        """
        Determine if button highlighting should be updated based on current state.

        Button highlighting is disabled during active game notifications.

        Args:
            program_state: The current program state (menu or game).

        Returns:
            True if highlighting should be updated, False otherwise.
        """
        # Only skip highlighting when in game mode with an active notification
        return not (program_state == ProgramState.GAME and self.model.notification is not None)

    def _update_highlight(self, cursor_position: Tuple[int, int]) -> None:
        """
        Update button highlighting based on cursor position.

        Highlights buttons when the cursor is over them and clears
        highlighting when the cursor moves away.

        Args:
            cursor_position: The current (x, y) position of the cursor.
        """
        if self.model.highlighted_button:
            if not self.model.highlighted_button.rect.collidepoint(cursor_position):
                self.model.clear_highlight()
                self.model_updated = True
        else:
            for button in self.model.active_buttons:
                if button.rect.collidepoint(cursor_position):
                    self.model.set_highlight(button.flag)
                    self.model_updated = True
                    break

    def _handle_start_gameplay(self) -> None:
        """
        Handle the transition from menu to game state.

        Sets the next_state flag to initiate the transition to game state.
        """
        self.next_state = ProgramState.GAME

    def _handle_enter_options(self) -> None:
        """
        Handle the transition to the options menu.

        Resets displayed settings to match current settings and
        updates the menu state.
        """
        self.model.reset_displayed_settings()
        self.model.update_menu_state(MenuState.OPTIONS)

    def _handle_program_exit(self) -> None:
        """
        Handle program exit request.

        Sets the exit_flag to initiate program termination.
        """
        self.exit_flag = True

    def _handle_accept_options(self) -> None:
        """
        Handle the acceptance of changed settings in the options menu.

        Sets appropriate flags if theme or resolution has changed,
        implements the displayed settings, and returns to the main menu.
        """
        if self.model.settings["theme"] != self.model.settings_select_display[0]:
            self.asset_package_updated = True
        if self.model.settings["resolution"] != self.model.settings_select_display[1]:
            self.resolution_updated = True
        self.model.implement_displayed_settings()
        self.model.update_menu_state(MenuState.MAIN)

    def _resolve_menu_click(self) -> None:
        """
        Handle click events in the menu system.

        Processes clicks in different menu states (main, options, tutorial, credits)
        and executes the appropriate action.
        """
        if self.model.current_menu == MenuState.CREDITS:
            self.model_updated = True
            self.model.update_menu_state(MenuState.MAIN)
            return

        if self.model.current_menu == MenuState.TUTORIAL:
            self.model_updated = True
            if self.model.tutorial_step():
                self.model.update_menu_state(MenuState.MAIN)
            return

        button_handlers = {ButtonFlag.PLAY: self._handle_start_gameplay,
                           ButtonFlag.OPTIONS: self._handle_enter_options,
                           ButtonFlag.EXIT: self._handle_program_exit,
                           ButtonFlag.ACCEPT_SETTINGS: self._handle_accept_options,
                           ButtonFlag.TUTORIAL: lambda: self.model.update_menu_state(MenuState.TUTORIAL),
                           ButtonFlag.CREDITS: lambda: self.model.update_menu_state(MenuState.CREDITS),
                           ButtonFlag.BACK_TO_MAIN: lambda: self.model.update_menu_state(MenuState.MAIN),
                           ButtonFlag.DIFFICULTY_TOGGLE: lambda: self.model.cycle_difficulty_displayed(),
                           ButtonFlag.RESOLUTION_TOGGLE: lambda: self.model.cycle_resolution_displayed(),
                           ButtonFlag.THEME_TOGGLE: lambda: self.model.cycle_theme_displayed()
                           }

        if self.model.highlighted_button:
            self.model_updated = True
            current_flag = self.model.highlighted_button.flag
            button_handlers[current_flag]()

    def _resolve_notification(self) -> None:
        """
        Handle click events when a game notification is active.

        Processes victory notifications by transitioning to the menu state,
        or clears other notifications to continue gameplay.
        """
        if self.model.notification == GameNotification.VICTORY:
            self.next_state = ProgramState.MENU
        else:
            self.model.clear_notification()
            self.model_updated = True

    def _handle_game_button_click(self) -> None:
        """
        Handle clicks on game interface buttons.

        Processes clicks on the reset board and back to main menu buttons.
        """
        self.model_updated = True
        if self.model.highlighted_button.flag == ButtonFlag.BACK_TO_MAIN:
            self.next_state = ProgramState.MENU
        if self.model.highlighted_button.flag == ButtonFlag.RESET_BOARD:
            self.model.reset_board()


    def _find_clicked_tower(self, position: Tuple[int, int]) -> int:
        """
        Determine which tower was clicked based on horizontal position.

        Args:
            position: The (x, y) coordinates of the click.

        Returns:
            The index of the clicked tower (0, 1, or 2).
        """
        if position[0] < self.LEFT_TOWER_BOUNDARY:
            return 0
        elif position[0] > self.RIGHT_TOWER_BOUNDARY:
            return 2
        else:
            return 1

    def _attempt_tower_select(self, clicked_tower: int) -> None:
        """
        Attempt to select a tower when no tower is currently selected.

        Only allows selection of towers that have discs on them.

        Args:
            clicked_tower: The index of the tower to select.
        """
        if self.model.towers[clicked_tower]:
            self.model_updated = True
            self.model.set_selected_tower(clicked_tower)

    def _execute_move(self, clicked_tower: int) -> None:
        """
        Execute a validated disc move and check for victory.

        Moves a disc from the selected tower to the clicked tower,
        clears the tower selection, and checks if the puzzle is complete.

        Args:
            clicked_tower: The destination tower index.
        """
        self.model.move_disc(self.model.selected_tower, clicked_tower)
        self.model.set_selected_tower(None)
        if self.model.is_complete():
            self.model.set_notification(GameNotification.VICTORY)

    def _handle_second_tower_click(self, clicked_tower: int) -> None:
        """
        Handle clicks when a tower is already selected.

        Either deselects the current tower, executes a legal move,
        or displays an illegal move notification.

        Args:
            clicked_tower: The index of the newly clicked tower.
        """
        if self.model.selected_tower == clicked_tower:
            self.model.set_selected_tower(None)
        else:
            if self.model.check_move_legal(self.model.selected_tower, clicked_tower):
                self._execute_move(clicked_tower)
            else:
                self.model.set_notification(GameNotification.ILLEGAL_MOVE)

    def _handle_tower_interaction(self, clicked_tower: int) -> None:
        """
        Handle interactions with towers during gameplay.

        Either attempts to select a tower or handles interactions
        with a second tower when one is already selected.

        Args:
            clicked_tower: The index of the clicked tower.
        """
        if self.model.selected_tower is None:
            self._attempt_tower_select(clicked_tower)
        else:
            self.model_updated = True
            self._handle_second_tower_click(clicked_tower)

    def _resolve_gameboard_click(self, cursor_position: Tuple[int, int]) -> None:
        """
        Handle click events in the game board.

        Processes clicks based on the current game state: notification active,
        button highlighted, or direct tower interaction.

        Args:
            cursor_position: The (x, y) coordinates of the click.
        """
        if self.model.notification is not None:
            self._resolve_notification()
            return

        if self.model.highlighted_button:
            self._handle_game_button_click()
            return

        clicked_tower = self._find_clicked_tower(cursor_position)
        self._handle_tower_interaction(clicked_tower)

    def handle_input(self, user_input: UserInput, program_state: ProgramState) -> None:
        """
        Process user input and update the active model accordingly.

        This main entry point handles cursor movements for button highlighting
        and clicks for executing actions based on the current program state.

        Args:
            user_input: Object containing position and click information.
            program_state: The current state of the program (menu or game).
        """
        if self._should_update_highlight(program_state):
            self._update_highlight(user_input.position)

        if user_input.clicked:
            if program_state == ProgramState.MENU:
                self._resolve_menu_click()
            elif program_state == ProgramState.GAME:
                self._resolve_gameboard_click(user_input.position)
