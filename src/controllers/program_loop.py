import pygame
import sys
import logging
from src.models.menu_model import MenuModel
from src.models.game_model import GameModel
from src.views.assets import build_asset_container
from src.views.renderer import GameRenderer
from .controller import ProgramController
from src.constants import MenuTheme, MenuState, ProgramState, UserInput
from typing import List, Tuple


logger = logging.getLogger(__name__)


class ProgramLoop:
    """
    Manages the main execution loop that drives the Tower of Hanoi application.

    This class initializes Pygame, creates the virtual screen architecture,
    coordinates state transitions, and maintains the game loop that processes
    input, updates models, and renders the screen.

    Attributes:
        screen: The main Pygame display surface.
        virtual_screen: Fixed-size surface for resolution-independent rendering.
        menu_model: Persistent MenuModel instance used throughout the program.
        renderer: GameRenderer instance for drawing to the screen.
        controller: ProgramController for handling user input.
        current_state: Current program state (menu or game).
        clock: Pygame clock for controlling frame rate.
        running: Flag indicating if the program should continue running.
        VIRTUAL_SCREEN_SIZE: Fixed dimensions of the virtual screen.
        PROGRAM_FPS: Target frames per second for the game loop.
    """
    # Class constants
    VIRTUAL_SCREEN_SIZE = (960, 640)
    PROGRAM_FPS = 60

    def __init__(self):
        """
        Initialize the program loop and all core components.

        Sets up Pygame, creates the display surfaces, initializes the menu model,
        loads assets, and creates the renderer and controller instances.

        Raises:
            SystemExit: If Pygame initialization fails or assets cannot be loaded.
        """
        try:
            pygame.init()
            self.screen = pygame.display.set_mode(self.VIRTUAL_SCREEN_SIZE)
            self.virtual_screen = pygame.Surface(self.VIRTUAL_SCREEN_SIZE)

            self.menu_model = MenuModel()

            asset_container = build_asset_container(MenuTheme.STANDARD)
            if asset_container is None:
                print("Failed to load assets")
                pygame.quit()
                sys.exit(1)

            self.renderer = GameRenderer(asset_container)
            self.controller = ProgramController(self.menu_model)
            self.current_state = ProgramState.MENU
            self.clock = pygame.time.Clock()
            self.running = True

            pygame.display.set_caption("Towers of Hanoi")

        except pygame.error as e:
            logger.error(f"Failed to initialize pygame: {e}")
            sys.exit(1)


    @staticmethod
    def _check_for_exit_events(event_list: List[pygame.event.Event]) -> bool:
        """
        Check if any exit events (window close) have occurred.

        Args:
            event_list: List of Pygame events to check.

        Returns:
            True if an exit event was found, False otherwise.
        """
        for event in event_list:
            if event.type == pygame.QUIT:
                return True
        return False

    def process_input(self, event_list: List[pygame.event.Event]) -> UserInput:
        """
        Process raw Pygame events into a structured UserInput object.

        Converts physical screen coordinates to virtual screen coordinates
        and detects mouse clicks.

        Args:
            event_list: List of Pygame events to process.

        Returns:
            UserInput object with position and click information.
        """
        mouse_pos = pygame.mouse.get_pos()
        virtual_width, virtual_hight = self.VIRTUAL_SCREEN_SIZE
        current_width, current_hight = self.screen.get_size()

        virtual_x = mouse_pos[0] * virtual_width // current_width
        virtual_y = mouse_pos[1] * virtual_hight // current_hight
        virtual_mouse_pos = (virtual_x, virtual_y)

        clicked = False
        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN:
                clicked = True
                break

        return UserInput(position=virtual_mouse_pos, clicked=clicked)

    def handle_user_input(self) -> bool:
        """
        Get and process user input events.

        Checks for exit events, processes input into a UserInput object,
        and passes it to the controller for handling.

        Returns:
            False if the program should exit, True otherwise.
        """
        event_list = pygame.event.get()
        if self._check_for_exit_events(event_list):
            return False
        user_input = self.process_input(event_list)
        self.controller.handle_input(user_input, self.current_state)
        return not self.controller.exit_flag


    def check_and_update_settings(self) -> None:
        """
        Check for and apply settings changes.

        Updates the asset container if the theme has changed and
        updates the display mode if the resolution has changed.
        """
        if self.controller.asset_package_updated:
            active_theme = self.controller.model.settings["theme"]
            new_container = build_asset_container(active_theme)
            self.renderer.update_assets(new_container)

        if self.controller.resolution_updated:
            active_resolution = self.controller.model.settings["resolution"]
            self.screen = pygame.display.set_mode(active_resolution)

        self.controller.reset_settings_update_flags()

    def handle_program_state_change(self) -> None:
        """
        Handle transitions between menu and game states.

        Creates a new GameModel when transitioning to the game state or
        switches back to the persistent MenuModel when returning to the menu.
        """
        if self.controller.next_state is not None:
            self.current_state = self.controller.next_state
            if self.current_state == ProgramState.MENU:
                new_model = self.menu_model
            else:
                active_difficulty = self.controller.model.settings["difficulty"]
                new_model = GameModel(active_difficulty)
            self.controller.update_state(new_model)

    def update_and_render(self) -> None:
        """
        Update the display if the model has changed.

        Renders the appropriate view based on the current state, scales
        the virtual screen to the actual display size, and updates the screen.
        """
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
        """
        Execute the main program loop.

        Handles input processing, state changes, rendering, and timing in a
        continuous loop until the program is terminated.
        """
        self.controller.model_updated = True
        self.update_and_render()

        while self.running:
            self.running = self.handle_user_input()
            self.check_and_update_settings()
            self.handle_program_state_change()
            self.update_and_render()
            self.clock.tick(self.PROGRAM_FPS)

        pygame.quit()
