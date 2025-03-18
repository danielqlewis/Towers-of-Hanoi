import pygame
from src.models.menu_model import MenuModel
from src.models.game_model import GameModel
from src.views.assets import build_asset_container
from src.views.renderer import GameRenderer
from .controller import ProgramController
from src.constants import MenuTheme, MenuState, ProgramState, UserInput
from typing import List, Tuple


class ProgramLoop:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((960, 640))
        self.virtual_screen = pygame.Surface((960, 640))
        self.menu_model = MenuModel()
        self.renderer = GameRenderer(build_asset_container(MenuTheme.STANDARD))
        self.controller = ProgramController(self.menu_model)
        self.current_state = ProgramState.MENU
        self.clock = pygame.time.Clock()
        self.running = True

    @staticmethod
    def _check_for_exit_events(event_list):
        for event in event_list:
            if event.type == pygame.QUIT:
                return True
        return False

    def process_input(self, event_list: List[pygame.event.Event]) -> UserInput:
        mouse_pos = pygame.mouse.get_pos()
        current_screen_size = self.screen.get_size()
        virtual_mouse_pos = (mouse_pos[0] * 960 // current_screen_size[0],
                             mouse_pos[1] * 640 // current_screen_size[1])
        clicked = False
        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN:
                clicked = True
                break
        return UserInput(position=virtual_mouse_pos, clicked=clicked)

    def handle_user_input(self):
        event_list = pygame.event.get()
        if self._check_for_exit_events(event_list):
            return False
        user_input = self.process_input(event_list)
        self.controller.handle_input(user_input, self.current_state)
        return not self.controller.exit_flag


    def check_and_update_settings(self):
        if self.controller.asset_package_updated:
            active_theme = self.controller.model.settings["theme"]
            self.renderer = GameRenderer(build_asset_container(active_theme))

        if self.controller.resolution_updated:
            active_resolution = self.controller.model.settings["resolution"]
            self.screen = pygame.display.set_mode(active_resolution)

        self.controller.reset_settings_update_flags()

    def handle_program_state_change(self):
        if self.controller.next_state is not None:
            self.current_state = self.controller.next_state
            if self.current_state == ProgramState.MENU:
                new_model = self.menu_model
            else:
                active_difficulty = self.controller.model.settings["difficulty"]
                new_model = GameModel(active_difficulty)
            self.controller.update_state(new_model)

    def update_and_render(self):
        if self.controller.model_updated:
            if self.current_state == ProgramState.MENU:
                self.renderer.render_menu(self.controller.model, self.virtual_screen)
            elif self.current_state == ProgramState.GAME:
                self.renderer.render_game(self.controller.model, self.virtual_screen)
            self.controller.reset_render_flag()
            current_screen_size = self.screen.get_size()
            scaled_screen = pygame.transform.smoothscale(self.virtual_screen, current_screen_size)
            self.screen.blit(scaled_screen, (0, 0))
            pygame.display.flip()

    def run_program(self) -> None:
        self.renderer.render_menu(self.controller.model, self.screen)
        pygame.display.flip()

        while self.running:
            self.running = self.handle_user_input()
            self.check_and_update_settings()
            self.handle_program_state_change()
            self.update_and_render()
            self.clock.tick(60)

        pygame.quit()
