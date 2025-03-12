import pygame
from models.menu_model import MenuModel
from models.game_model import GameModel
from assets import build_asset_container
from renderer import GameRenderer
from controller import ProgramController
from constants import MenuTheme, MenuState, ProgramState


class UserInput:
    def __init__(self, position=(0, 0), clicked=False):
        self.position = position  # (x, y) coordinates
        self.clicked = clicked


def process_input(event_list):
    position = pygame.mouse.get_pos()
    clicked = False
    for event in event_list:
        if event.type == pygame.MOUSEBUTTONDOWN:
            clicked = True
            break
    return UserInput(position, clicked)


def run_program():
    pygame.init()
    screen = pygame.display.set_mode((960, 640))

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

        user_input = process_input(event_list)
        controller.handle_input(user_input, current_state)

        if controller.exit_flag:
            break

        if controller.next_state is not None:
            current_state = controller.next_state
            if current_state == ProgramState.MENU:
                controller.model = menu_model
            elif current_state == ProgramState.GAME:
                controller.model = GameModel()
            controller.next_state = None
            controller.model_updated = True

        if controller.model_updated:
            if current_state == ProgramState.MENU:
                renderer.render_menu(controller.model, screen)
            elif current_state == ProgramState.GAME:
                renderer.render_game(controller.model, screen)
            pygame.display.flip()
            controller.model_updated = False

        clock.tick(60)

    pygame.quit()
