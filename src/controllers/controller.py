from src.constants import ProgramState, ButtonFlag, MenuState, GameNotification, UserInput
from src.models.menu_model import MenuModel
from typing import Tuple


class ProgramController:
    def __init__(self, model: MenuModel):
        self.model = model
        self.model_updated = False
        self.next_state = None
        self.exit_flag = False
        self.asset_package_updated = False
        self.resolution_updated = False

    def reset_settings_update_flags(self):
        self.asset_package_updated = False
        self.resolution_updated = False

    def reset_render_flag(self):
        self.model_updated = False

    def update_state(self, new_model):
        self.model = new_model
        self.next_state = None
        self.model_updated = True

    def _should_update_highlight(self, program_state: ProgramState) -> bool:
        # Only skip highlighting when in game mode with an active notification
        return not (program_state == ProgramState.GAME and self.model.notification is not None)

    def _update_highlight(self, cursor_position: Tuple[int, int]) -> None:
        if self.model.highlighted_button:
            if not self.model.highlighted_button.rect.collidepoint(cursor_position):
                self.model.deset_highlight()
                self.model_updated = True
        else:
            for button in self.model.active_buttons:
                if button.rect.collidepoint(cursor_position):
                    self.model.set_highlight(button.flag)
                    self.model_updated = True
                    break

    def _handle_start_gameplay(self):
        self.next_state = ProgramState.GAME

    def _handle_enter_options(self):
        self.model.reset_displayed_settings()
        self.model.update_menu_state(MenuState.OPTIONS)

    def _handle_program_exit(self):
        self.exit_flag = True

    def _handle_accept_options(self):
        if self.model.settings["theme"] != self.model.settings_select_display[0]:
            self.asset_package_updated = True
        if self.model.settings["resolution"] != self.model.settings_select_display[1]:
            self.resolution_updated = True
        self.model.implement_displayed_settings()
        self.model.update_menu_state(MenuState.MAIN)

    def _resolve_menu_click(self) -> None:
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

    def _resolve_notification(self):
        if self.model.notification == GameNotification.VICTORY:
            self.next_state = ProgramState.MENU
        else:
            self.model.deset_notification()
            self.model_updated = True

    def _handle_game_button_click(self):
        self.model_updated = True
        if self.model.highlighted_button.flag == ButtonFlag.BACK_TO_MAIN:
            self.next_state = ProgramState.MENU
        if self.model.highlighted_button.flag == ButtonFlag.RESET_BOARD:
            self.model.reset_board()

    @staticmethod
    def _find_clicked_tower(position: Tuple[int, int]) -> int:
        if position[0] < 320:
            return 0
        elif position[0] > 640:
            return 2
        else:
            return 1

    def _attempt_tower_select(self, clicked_tower):
        if self.model.towers[clicked_tower]:
            self.model_updated = True
            self.model.set_selected_tower(clicked_tower)

    def _execute_move(self, clicked_tower):
        self.model.move_disc(self.model.selected_tower, clicked_tower)
        self.model.set_selected_tower(None)
        if self.model.is_complete():
            self.model.set_notification(GameNotification.VICTORY)

    def _handle_second_tower_click(self, clicked_tower):
        if self.model.selected_tower == clicked_tower:
            self.model.set_selected_tower(None)
        else:
            if self.model.check_move_legal(self.model.selected_tower, clicked_tower):
                self._execute_move(clicked_tower)
            else:
                self.model.set_notification(GameNotification.ILLEGAL_MOVE)

    def _handle_tower_interaction(self, clicked_tower):
        if self.model.selected_tower is None:
            self._attempt_tower_select(clicked_tower)
        else:
            self.model_updated = True
            self._handle_second_tower_click(clicked_tower)

    def _resolve_gameboard_click(self, cursor_position: Tuple[int, int]) -> None:

        if self.model.notification is not None:
            self._resolve_notification()
            return

        if self.model.highlighted_button:
            self._handle_game_button_click()
            return

        clicked_tower = self._find_clicked_tower(cursor_position)
        self._handle_tower_interaction(clicked_tower)

    def handle_input(self, user_input: UserInput, program_state: ProgramState) -> None:
        if self._should_update_highlight(program_state):
            self._update_highlight(user_input.position)

        if user_input.clicked:
            if program_state == ProgramState.MENU:
                self._resolve_menu_click()
            elif program_state == ProgramState.GAME:
                self._resolve_gameboard_click(user_input.position)
