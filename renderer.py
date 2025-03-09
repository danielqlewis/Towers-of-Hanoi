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
        active_theme_indicator = self.assets.setting_indicators.theme[model.settings_select_display[0]]
        active_resolution_indicator = self.assets.setting_indicators.resolution[model.settings_select_display[1]]
        active_difficulty_indicator = self.assets.setting_indicators.difficulty[model.settings_select_display[2]]
        screen.blit(active_difficulty_indicator, [550, 160])
        screen.blit(active_resolution_indicator, [550, 300])
        screen.blit(active_theme_indicator, [550, 420])


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
        TOWER_CENTERX = [192, 480, 768]
        if highlight:
            active_image = self.assets.discs.highlighted[disc_size]
        else:
            active_image = self.assets.discs.standard[disc_size]
        active_x = TOWER_CENTERX[tower] - 43 - (21 * disc_size)
        active_y = 587 - 71 - (69 * height)
        screen.blit(active_image, [active_x, active_y])


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
