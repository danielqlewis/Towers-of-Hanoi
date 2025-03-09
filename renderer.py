import pygame
from constants import MenuState, ButtonFlag


class GameRenderer:
    def __init__(self, asset_container):
        self.assets = asset_container

    def _draw_menu_background(self, model, screen):
        if model.current_menu == MenuState.MAIN:
            background_image = self.assets.backgrounds.credits
        elif model.current_menu == MenuState.OPTIONS:
            background_image = self.assets.backgrounds.options_menu
        elif model.current_menu == MenuState.CREDITS:
            background_image = self.assets.backgrounds.credits
        else:
            background_image = pygame.Surface((0, 0))
        screen.blit(background_image, [0, 0])

    def _draw_menu_button(self, model, button, screen):
        if model.highlighed_button == button.flag:
            button_image = self.assets.buttons.highlighted[button.flag]
        else:
            button_image = self.assets.buttons.standard[button.flag]
        button_pos = button.rect.topleft
        screen.blit(button_image, button_pos)

    def _draw_tutorial(self, model, screen):
        slide_image = self.assets.tutorial_images[model.tutorial_slide]
        screen.blit(slide_image, [0, 0])

    def render_menu(self, model, screen):
        self._draw_menu_background(model, screen)
        for button in model.active_buttons:
            self._draw_menu_button(model, button, screen)
        if self.model.current_menu == MenuState.TUTORIAL:
            self._draw_tutorial(model, screen)

    def render_game(self, model, screen):
        pass
