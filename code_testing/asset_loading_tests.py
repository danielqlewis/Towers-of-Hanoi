from assets import build_asset_container, AssetsContainer
from constants import MenuTheme, Button
import pygame
import os
import sys


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_asset_container_creation():
    # Initialize pygame if not already done
    if not pygame.get_init():
        pygame.init()
        pygame.display.set_mode([0, 0])

    # Test default theme
    container = build_asset_container(MenuTheme.STANDARD)
    assert container is not None
    assert isinstance(container, AssetsContainer)

    # Check that the container has all expected components
    assert hasattr(container, 'backgrounds')
    assert hasattr(container, 'buttons')
    assert hasattr(container, 'discs')
    assert hasattr(container, 'setting_indicators')
    assert hasattr(container, 'game_notifications')
    assert hasattr(container, 'tutorial_images')


def test_asset_container_theme_specific():
    if not pygame.get_init():
        pygame.init()

    # Test all themes
    for theme in MenuTheme:
        container = build_asset_container(theme)
        assert container is not None

        # Each theme should have its own specific backgrounds
        assert hasattr(container.backgrounds, 'main_menu')
        assert hasattr(container.backgrounds, 'options_menu')
        assert hasattr(container.backgrounds, 'game_board')


def test_asset_container_buttons():
    if not pygame.get_init():
        pygame.init()

    container = build_asset_container(MenuTheme.STANDARD)

    # Check all buttons exist in both standard and highlighted states
    for button in Button:
        assert button in container.buttons.standard
        assert button in container.buttons.highlighted

        # Verify they're pygame surfaces
        assert isinstance(container.buttons.standard[button], pygame.Surface)
        assert isinstance(container.buttons.highlighted[button], pygame.Surface)


def test_asset_container_discs():
    if not pygame.get_init():
        pygame.init()

    container = build_asset_container(MenuTheme.STANDARD)

    # Check all disc sizes exist
    for disc_size in range(5):  # Assuming 5 disc sizes (0-4)
        assert disc_size in container.discs.standard
        assert disc_size in container.discs.highlighted

        # Verify they're pygame surfaces
        assert isinstance(container.discs.standard[disc_size], pygame.Surface)
        assert isinstance(container.discs.highlighted[disc_size], pygame.Surface)


def test_asset_container_setting_indicators():
    if not pygame.get_init():
        pygame.init()

    container = build_asset_container(MenuTheme.STANDARD)

    # Check difficulty indicators
    for difficulty in [3, 4, 5]:
        assert difficulty in container.setting_indicators.difficulty

    # Check resolution indicators
    resolutions = [(720, 480), (864, 576), (960, 640), (1080, 720), (1296, 864)]
    for resolution in resolutions:
        assert resolution in container.setting_indicators.resolution

    # Check theme indicators
    for theme in MenuTheme:
        assert theme in container.setting_indicators.theme