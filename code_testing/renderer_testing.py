import pygame
import os
import sys
from models.menu_model import MenuModel
from assets import build_asset_container
from renderer import GameRenderer
from constants import MenuTheme, MenuState, ButtonFlag

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_renderer():
    # Initialize pygame
    pygame.init()

    # Set up the display
    width, height = 960, 640
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Renderer Test")

    # Set up your game objects
    active_model = MenuModel()
    active_model.update_menu_state(MenuState.OPTIONS)
    active_model.highlighted_button = ButtonFlag.ACCEPT_SETTINGS
    asset_package = build_asset_container(MenuTheme.STANDARD)
    renderer = GameRenderer(asset_package)

    # Clear screen with a background color
    screen.fill((0, 0, 0))  # Black background

    # Pass the screen to your renderer
    renderer.render_menu(active_model, screen)

    # Update the display to show what was rendered
    pygame.display.flip()

    # Keep the window open until closed
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    # Clean up
    pygame.quit()


if __name__ == "__main__":
    test_renderer()
