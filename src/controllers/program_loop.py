import pygame
from src.models.menu_model import MenuModel
from src.models.game_model import GameModel
from src.views.assets import build_asset_container
from src.views.renderer import GameRenderer
from .controller import ProgramController
from src.constants import MenuTheme, MenuState, ProgramState, UserInput
from typing import List, Tuple





def process_input(event_list: List[pygame.event.Event], current_screen_size: Tuple[int, int]) -> UserInput:
    mouse_pos = pygame.mouse.get_pos()
    virtual_mouse_pos = (mouse_pos[0] * 960 // current_screen_size[0],
                         mouse_pos[1] * 640 // current_screen_size[1])
    clicked = False
    for event in event_list:
        if event.type == pygame.MOUSEBUTTONDOWN:
            clicked = True
            break
    return UserInput(position=virtual_mouse_pos, clicked=clicked)


def run_program() -> None:
    pygame.init()
    screen = pygame.display.set_mode((960, 640))
    virtual_screen = pygame.Surface((960, 640))

    menu_model = MenuModel()
    menu_model.update_menu_state(MenuState.MAIN)
    renderer = GameRenderer(build_asset_container(MenuTheme.STANDARD))
    controller = ProgramController(menu_model)

    current_state = ProgramState.MENU

    running = True
    clock = pygame.time.Clock()

    renderer.render_menu(controller.model, screen)
    pygame.display.flip()

    while running:
        event_list = pygame.event.get()
        quit_events = [event for event in event_list if event.type == pygame.QUIT]
        if quit_events:
            break

        user_input = process_input(event_list, screen.get_size())
        controller.handle_input(user_input, current_state)

        if controller.exit_flag:
            break

        if controller.asset_package_updated:
            active_theme = controller.model.settings["theme"]
            renderer = GameRenderer(build_asset_container(active_theme))
            controller.asset_package_updated = False

        if controller.resolution_updated:
            active_resolution = controller.model.settings["resolution"]
            screen = pygame.display.set_mode(active_resolution)
            controller.resolution_updated = False

        if controller.next_state is not None:
            current_state = controller.next_state
            if current_state == ProgramState.MENU:
                controller.model = menu_model
            elif current_state == ProgramState.GAME:
                active_difficulty = controller.model.settings["difficulty"]
                controller.model = GameModel(active_difficulty)
            controller.next_state = None
            controller.model_updated = True

        if controller.model_updated:
            if current_state == ProgramState.MENU:
                renderer.render_menu(controller.model, virtual_screen)
            elif current_state == ProgramState.GAME:
                renderer.render_game(controller.model, virtual_screen)
            current_screen_size = screen.get_size()
            scaled_screen = pygame.transform.smoothscale(virtual_screen, current_screen_size)
            screen.blit(scaled_screen, (0, 0))
            pygame.display.flip()
            controller.model_updated = False

        clock.tick(60)

    pygame.quit()
