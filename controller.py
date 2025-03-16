from constants import ProgramState, ButtonFlag, MenuState, GameNotification


class ProgramController:
    def __init__(self, model):
        self.model = model
        self.model_updated = False
        self.next_state = None
        self.exit_flag = False
        self.asset_package_updated = False
        self.resolution_updated = False

    def _update_highlight(self, cursor_position):
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

    def _resolve_menu_click(self):

        if self.model.current_menu == MenuState.CREDITS:
            self.model_updated = True
            self.model.update_menu_state(MenuState.MAIN)

        if self.model.current_menu == MenuState.TUTORIAL:
            self.model_updated = True
            if self.model.tutorial_step():
                self.model.update_menu_state(MenuState.MAIN)

        if self.model.highlighted_button:
            self.model_updated = True
            if self.model.highlighted_button.flag == ButtonFlag.PLAY:
                self.next_state = ProgramState.GAME
            elif self.model.highlighted_button.flag == ButtonFlag.OPTIONS:
                self.model.reset_displayed_settings()
                self.model.update_menu_state(MenuState.OPTIONS)
            elif self.model.highlighted_button.flag == ButtonFlag.EXIT:
                self.exit_flag = True
            elif self.model.highlighted_button.flag == ButtonFlag.TUTORIAL:
                self.model.update_menu_state(MenuState.TUTORIAL)
            elif self.model.highlighted_button.flag == ButtonFlag.CREDITS:
                self.model.update_menu_state(MenuState.CREDITS)

            elif self.model.highlighted_button.flag == ButtonFlag.DIFFICULTY_TOGGLE:
                self.model.cycle_difficulty_displayed()
            elif self.model.highlighted_button.flag == ButtonFlag.RESOLUTION_TOGGLE:
                self.model.cycle_resolution_displayed()
            elif self.model.highlighted_button.flag == ButtonFlag.THEME_TOGGLE:
                self.model.cycle_theme_displayed()
            elif self.model.highlighted_button.flag == ButtonFlag.BACK_TO_MAIN:
                self.model.update_menu_state(MenuState.MAIN)
            elif self.model.highlighted_button.flag == ButtonFlag.ACCEPT_SETTINGS:
                if self.model.settings["theme"] != self.model.settings_select_display[0]:
                    self.asset_package_updated = True
                if self.model.settings["resolution"] != self.model.settings_select_display[1]:
                    self.resolution_updated = True
                self.model.implement_displayed_settings()
                self.model.update_menu_state(MenuState.MAIN)

    def _resolve_gameboard_click(self, cursor_position):

        if self.model.notification is not None:
            if self.model.notification == GameNotification.VICTORY:
                self.next_state = ProgramState.MENU
            else:
                self.model.deset_notification()
                self.model_updated = True
        else:
            if self.model.highlighted_button:
                self.model_updated = True
                if self.model.highlighted_button.flag == ButtonFlag.BACK_TO_MAIN:
                    self.next_state = ProgramState.MENU
                if self.model.highlighted_button.flag == ButtonFlag.RESET_BOARD:
                    self.model.reset_board()
            else:
                if cursor_position[0] < 320:
                    clicked_tower = 0
                elif cursor_position[0] > 640:
                    clicked_tower = 2
                else:
                    clicked_tower = 1

                if self.model.selected_tower is None:
                    if self.model.towers[clicked_tower]:
                        self.model_updated = True
                        self.model.selected_tower = clicked_tower
                else:
                    self.model_updated = True
                    if self.model.selected_tower == clicked_tower:
                        self.model.selected_tower = None
                    else:
                        if self.model.check_move_legal(self.model.selected_tower, clicked_tower):
                            self.model.move_disc(self.model.selected_tower, clicked_tower)
                            self.model.selected_tower = None
                            if self.model.is_complete():
                                self.model.set_notification(GameNotification.VICTORY)
                        else:
                            self.model.set_notification(GameNotification.ILLEGAL_MOVE)

    def handle_input(self, user_input, program_state):
        skip_highlight = False
        if program_state == ProgramState.GAME:
            if self.model.notification is not None:
                skip_highlight = True
        if not skip_highlight:
            self._update_highlight(user_input.position)
        if user_input.clicked:
            if program_state == ProgramState.MENU:
                self._resolve_menu_click()
            elif program_state == ProgramState.GAME:
                self._resolve_gameboard_click(user_input.position)
