import pygame
from constants import MenuState, ButtonFlag


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
        if model.highlighted_button == button.flag:
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
        slide_image = self.assets.tutorial_images[model.tutorial_slide]
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

    def render_game(self, model, screen):
        background_image = self.assets.backgrounds.game_board
        screen.blit(background_image, [0, 0])
        self._draw_game_discs(model, screen)
        for button in model.active_buttons:
            self._draw_button(model, button, screen)
