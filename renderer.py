import pygame
from constants import MenuState, Button

MAIN_MENU_BUTTON_LOCATIONS = {Button.PLAY: (0, 0),
                              Button.OPTIONS: (0, 0),
                              Button.EXIT: (0, 0),
                              Button.TUTORIAL: (0, 0),
                              Button.CREDITS: (0, 0)}
OPTIONS_MENU_BUTTON_LOCATIONS = {Button.DIFFICULTY_TOGGLE: (0, 0),
                                 Button.RESOLUTION_TOGGLE: (0, 0),
                                 Button.THEME_TOGGLE: (0, 0),
                                 Button.ACCEPT_SETTINGS: (0, 0),
                                 Button.BACK_TO_MAIN: (0, 0)}


class GameRenderer:
    def __init__(self, asset_container):
        self.assets = asset_container

    def draw_menu_background(self, model, screen):
        if model.current_menu == MenuState.OPTIONS:
            background_image = self.assets.backgrounds.options_menu
        elif model.current_menu == MenuState.CREDITS:
            background_image = self.assets.backgrounds.credits
        else:
            background_image = self.assets.backgrounds.main_menu
        screen.blit(background_image, [0, 0])

    def draw_menu_button(self, model, button, screen, highlight=False):
        if model.current_menu == MenuState.OPTIONS:
            location_map = OPTIONS_MENU_BUTTON_LOCATIONS
        else:
            location_map = MAIN_MENU_BUTTON_LOCATIONS
        location = location_map[button]
        if highlight:
            button_image = self.assets.buttons.highlighted[button]
        else:
            button_image = self.assets.buttons.standard[button]
        screen.blit(button_image, location)


    def draw_tutorial(self, model, screen):
        slide_image = self.assets.tutorial_images[model.tutorial_slide]
        screen.blit(slide_image, [0, 0])

    def render_menu(self, model, screen):
        self.draw_menu_background(model, screen)
        active_buttons = []
        if model.current_menu == MenuState.MAIN:
            active_buttons = [Button.PLAY, Button.OPTIONS, Button.TUTORIAL, Button.CREDITS, Button.EXIT]
        elif model.current_menu == MenuState.OPTIONS:
            active_buttons = [Button.DIFFICULTY_TOGGLE, Button.RESOLUTION_TOGGLE, Button.THEME_TOGGLE,
                              Button.ACCEPT_SETTINGS, Button.BACK_TO_MAIN]
        for button in active_buttons:
            highlight = False
            if model.highlighted_button == button:
                highlight = True
            self.draw_menu_button(model, button, screen, highlight)
        if model.current_menu == MenuState.TUTORIAL:
            self.draw_tutorial(model, screen)

    def render_game(self, model, screen):
        pass
