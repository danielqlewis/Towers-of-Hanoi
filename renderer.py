import pygame
from constants import MenuState, ButtonFlag, GameNotification


class GameRenderer:
    def __init__(self, asset_container):
        self.assets = asset_container

    def _draw_menu_background(self, model, screen):
        if model.current_menu == MenuState.MAIN:
            background_image = self.assets.backgrounds.main_menu
        elif model.current_menu == MenuState.OPTIONS:
            background_image = self.assets.backgrounds.options_menu
        elif model.current_menu == MenuState.CREDITS:
            background_image = self.assets.backgrounds.credits
        else:
            background_image = pygame.Surface((0, 0))
        screen.blit(background_image, [0, 0])

    def _draw_button(self, model, button, screen):
        button_highlighted = False
        if model.highlighted_button:
            if model.highlighted_button.flag == button.flag:
                button_highlighted = True

        if button_highlighted:
            button_image = self.assets.buttons.highlighted[button.flag]
        else:
            button_image = self.assets.buttons.standard[button.flag]
        button_pos = button.rect.topleft
        screen.blit(button_image, button_pos)

    def _draw_settings_indicators(self, model, screen):
        INDICATOR_POSITIONS = {
            "difficulty": (550, 160),
            "resolution": (550, 300),
            "theme": (550, 420)
        }

        theme_indicator = self.assets.setting_indicators.theme[model.settings_select_display[0]]
        resolution_indicator = self.assets.setting_indicators.resolution[model.settings_select_display[1]]
        difficulty_indicator = self.assets.setting_indicators.difficulty[model.settings_select_display[2]]

        screen.blit(difficulty_indicator, INDICATOR_POSITIONS["difficulty"])
        screen.blit(resolution_indicator, INDICATOR_POSITIONS["resolution"])
        screen.blit(theme_indicator, INDICATOR_POSITIONS["theme"])


    def _draw_tutorial(self, model, screen):
        slide_image = self.assets.tutorial_images.slides[model.tutorial_slide]
        screen.blit(slide_image, [0, 0])

    def render_menu(self, model, screen):
        self._draw_menu_background(model, screen)
        for button in model.active_buttons:
            self._draw_button(model, button, screen)
        if model.current_menu == MenuState.OPTIONS:
            self._draw_settings_indicators(model, screen)
        if model.current_menu == MenuState.TUTORIAL:
            self._draw_tutorial(model, screen)

    def _draw_single_disc(self, tower, disc_size, height, highlight, screen):
        TOWER_CENTERS = [192, 480, 768]  # X-coordinates of tower centers
        BASE_DISC_WIDTH = 43  # Half-width of the smallest disc
        DISC_WIDTH_INCREMENT = 21  # How much wider each size gets
        DISC_HEIGHT = 69  # Height of each disc
        BASE_Y = 516  # Y-coordinate of the top of the lowest disc

        # Select the appropriate disc image
        disc_image = self.assets.discs.highlighted[disc_size] if highlight else self.assets.discs.standard[disc_size]

        # Calculate positions
        x_position = TOWER_CENTERS[tower] - BASE_DISC_WIDTH - (DISC_WIDTH_INCREMENT * disc_size)
        y_position = BASE_Y - (DISC_HEIGHT * height)

        # Draw the disc
        screen.blit(disc_image, [x_position, y_position])


    def _draw_game_discs(self, model, screen):
        for tower_indx in range(3):
            active_tower = model.towers[tower_indx]
            for disc_indx in range(len(active_tower)):
                if model.selected_tower == tower_indx and active_tower[disc_indx] == active_tower[-1]:
                    highlight = True
                else:
                    highlight = False
                self._draw_single_disc(tower_indx, active_tower[disc_indx], disc_indx, highlight, screen)

    def _draw_game_notification(self, model, screen):
        if model.notification == GameNotification.ILLEGAL_MOVE:
            notification_image = self.assets.game_notifications.illegal_move
            notification_top = 20
        elif model.notification == GameNotification.VICTORY:
            notification_image = self.assets.game_notifications.victory
            notification_top = 160
        else:
            print("Critical Error")
            return

        image_size = notification_image.get_size()
        notifcation_location = [480 - (image_size[0] // 2), notification_top]
        screen.blit(notification_image, notifcation_location)

    def render_game(self, model, screen):
        background_image = self.assets.backgrounds.game_board
        screen.blit(background_image, [0, 0])
        self._draw_game_discs(model, screen)
        for button in model.active_buttons:
            self._draw_button(model, button, screen)
        if model.notification is not None:
            self._draw_game_notification(model, screen)
