import pygame
import os
import sys
from src.models.game_model import GameModel
from src.views.assets import build_asset_container
from src.views.renderer import GameRenderer
from src.constants import MenuTheme, GameNotification

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
    active_model = GameModel()
    active_model.notification = GameNotification.VICTORY
    asset_package = build_asset_container(MenuTheme.STANDARD)
    renderer = GameRenderer(asset_package)


    # Clear screen with a background color
    screen.fill((0, 0, 0))  # Black background

    # Pass the screen to your renderer
    renderer.render_game(active_model, screen)

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
