from dataclasses import dataclass
import pygame
import logging
from typing import Dict, Tuple, TypedDict, Optional
from src.constants import MenuTheme, ButtonFlag
from src.utils.asset_loader import load_image, load_image_with_alpha


logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class BackgroundContainer:
    """
    Container for background images used across different game states.

    Attributes:
        main_menu: Background image for the main menu screen.
        options_menu: Background image for the options menu screen.
        game_board: Background image for the game board screen.
        credits: Background image for the credits screen.
    """
    main_menu: pygame.Surface
    options_menu: pygame.Surface
    game_board: pygame.Surface
    credits: pygame.Surface


@dataclass(frozen=True)
class ButtonContainer:
    """
    Container for button images in normal and highlighted states.

    Attributes:
        standard: Dictionary mapping ButtonFlag enums to normal button images.
        highlighted: Dictionary mapping ButtonFlag enums to highlighted button images.
    """
    standard: Dict[ButtonFlag, pygame.Surface]
    highlighted: Dict[ButtonFlag, pygame.Surface]


@dataclass(frozen=True)
class DiscContainer:
    """
    Container for disc images in normal and highlighted states.

    Attributes:
        standard: Dictionary mapping disc sizes (integers) to normal disc images.
        highlighted: Dictionary mapping disc sizes (integers) to highlighted disc images.
    """
    standard: Dict[int, pygame.Surface]
    highlighted: Dict[int, pygame.Surface]


@dataclass(frozen=True)
class SettingIndicatorContainer:
    """
    Container for images that visualize user settings in the options menu.

    Attributes:
        difficulty: Dictionary mapping difficulty levels to corresponding indicator images.
        resolution: Dictionary mapping resolution tuples to corresponding indicator images.
        theme: Dictionary mapping MenuTheme enums to corresponding indicator images.
    """
    difficulty: Dict[int, pygame.Surface]
    resolution: Dict[Tuple, pygame.Surface]
    theme: Dict[MenuTheme, pygame.Surface]


@dataclass(frozen=True)
class GameNotificationContainer:
    """
    Container for notification images displayed during gameplay.

    Attributes:
        illegal_move: Image displayed when a player attempts an illegal move.
        victory: Image displayed when the player completes the puzzle.
    """
    illegal_move: pygame.Surface
    victory: pygame.Surface


@dataclass(frozen=True)
class TutorialSlidesContainer:
    """
    Container for tutorial slide images.

    Attributes:
        slides: Dictionary mapping slide indices to the corresponding tutorial images.
    """
    slides: Dict[int, pygame.Surface]


@dataclass(frozen=True)
class AssetsContainer:
    """
    Top-level container that organizes all game assets by category.

    This immutable container holds references to all visual resources used
    in the application, grouped by their functional purpose.

    Attributes:
        backgrounds: Container for all background images.
        buttons: Container for all button images.
        discs: Container for all disc images.
        setting_indicators: Container for all setting indicator images.
        game_notifications: Container for all notification images.
        tutorial_images: Container for all tutorial slides.
    """
    backgrounds: BackgroundContainer
    buttons: ButtonContainer
    discs: DiscContainer
    setting_indicators: SettingIndicatorContainer
    game_notifications: GameNotificationContainer
    tutorial_images: TutorialSlidesContainer


class CommonAssets(TypedDict):
    """
    TypedDict defining the structure for assets shared across all themes.

    Used as a return type for the get_common_assets function.

    Attributes:
        credits: Credits screen background image.
        button_assets: Container for all button images.
        disc_assets: Container for all disc images.
        setting_indicator_assets: Container for all setting indicator images.
        notification_assets: Container for all notification images.
        tutorial_assets: Container for all tutorial slides.
    """
    credits: pygame.Surface
    button_assets: ButtonContainer
    disc_assets: DiscContainer
    setting_indicator_assets: SettingIndicatorContainer
    notification_assets: GameNotificationContainer
    tutorial_assets: TutorialSlidesContainer


def get_theme_specific_assets(theme: MenuTheme) -> Tuple[pygame.Surface, pygame.Surface, pygame.Surface]:
    """
    Load the background images specific to the selected theme.

    Args:
        theme: The MenuTheme enum value representing the selected theme.

    Returns:
        A tuple containing (main_menu, options_menu, game_board) background surfaces.

    Raises:
        pygame.error: If an image cannot be loaded.
        FileNotFoundError: If an asset file is missing.
    """
    if theme == MenuTheme.RED:
        main_menu = load_image("red/Menu_BG.png")
        options_menu = load_image("red/Options_BG.png")
        game_board = load_image("red/Game_BG.png")
    elif theme == MenuTheme.BLUE:
        main_menu = load_image("blue/Menu_BG.png")
        options_menu = load_image("blue/Options_BG.png")
        game_board = load_image("blue/Game_BG.png")
    else:
        main_menu = load_image("default/Menu_BG.png")
        options_menu = load_image("default/Options_BG.png")
        game_board = load_image("default/Game_BG.png")

    return main_menu, options_menu, game_board


def get_common_assets() -> CommonAssets:
    """
    Load all assets that are shared across themes.

    This includes buttons, discs, setting indicators, notification images,
    and tutorial slides.

    Returns:
        A CommonAssets dictionary containing all shared asset containers.

    Raises:
        pygame.error: If an image cannot be loaded.
        FileNotFoundError: If an asset file is missing.
    """
    credits_background = load_image("Credit_Page.png")

    # Buttons###########################################################################################################
    button_mapping = {
        ButtonFlag.PLAY: "Play",
        ButtonFlag.OPTIONS: "Options",
        ButtonFlag.EXIT: "Exit",
        ButtonFlag.TUTORIAL: "Tutorial",
        ButtonFlag.CREDITS: "Credits",
        ButtonFlag.DIFFICULTY_TOGGLE: "Difficulty",
        ButtonFlag.RESOLUTION_TOGGLE: "Resolution",
        ButtonFlag.THEME_TOGGLE: "Style",
        ButtonFlag.BACK_TO_MAIN: "Back",
        ButtonFlag.ACCEPT_SETTINGS: "Accept",
        ButtonFlag.RESET_BOARD: "Refresh"
    }

    standard_buttons = {}
    highlighted_buttons = {}

    for button_flag, button_name in button_mapping.items():
        standard_buttons[button_flag] = load_image(f"{button_name}_Button_Base.png")
        highlighted_buttons[button_flag] = load_image(f"{button_name}_Button_Selected.png")

    local_buttons = ButtonContainer(standard=standard_buttons, highlighted=highlighted_buttons)

    # Discs#############################################################################################################
    standard_discs = {}
    highlighted_discs = {}

    for i in range(5):
        standard_discs[i] = load_image(f"Plate_{i}_b.png")
        highlighted_discs[i] = load_image(f"Plate_{i}_s.png")

    local_discs = DiscContainer(standard=standard_discs, highlighted=highlighted_discs)

    # Indicators########################################################################################################
    difficulty_indicators = {3: load_image("Difficulty_Display_1.png"),
                             4: load_image("Difficulty_Display_2.png"),
                             5: load_image("Difficulty_Display_3.png")}

    resolution_indicators = {(720, 480): load_image("Resolution_Display_1.png"),
                             (864, 576): load_image("Resolution_Display_2.png"),
                             (960, 640): load_image("Resolution_Display_3.png"),
                             (1080, 720): load_image("Resolution_Display_4.png"),
                             (1296, 864): load_image("Resolution_Display_5.png")}

    theme_indicators = {MenuTheme.STANDARD: load_image("Style_Display_1.png"),
                        MenuTheme.RED: load_image("Style_Display_2.png"),
                        MenuTheme.BLUE: load_image("Style_Display_3.png")}

    local_setting_indicators = SettingIndicatorContainer(difficulty=difficulty_indicators,
                                                         resolution=resolution_indicators,
                                                         theme=theme_indicators)

    # Notifications#####################################################################################################
    illegal_move_image = load_image_with_alpha("Big_X.png")
    victory_image = load_image_with_alpha("Victory.png")
    local_notificatons = GameNotificationContainer(illegal_move=illegal_move_image, victory=victory_image)

    # Tutorial##########################################################################################################
    tutorial_slides = {}
    for i in range(8):
        tutorial_slides[i] = load_image(f"Tutorial_{i + 1}.png")

    local_tutorials = TutorialSlidesContainer(slides=tutorial_slides)

    return {
        "credits": credits_background,
        "button_assets": local_buttons,
        "disc_assets": local_discs,
        "setting_indicator_assets": local_setting_indicators,
        "notification_assets": local_notificatons,
        "tutorial_assets": local_tutorials
    }


def build_asset_container(theme: MenuTheme) -> Optional[AssetsContainer]:
    """
    Create a complete AssetsContainer with all visual resources.

    This factory function assembles both theme-specific and common assets
    into a single immutable container for use by the renderer.

    Args:
        theme: The MenuTheme enum value representing the selected theme.

    Returns:
        A complete AssetsContainer with all assets, or None if loading fails.

    Raises:
        No exceptions are raised directly - errors are logged instead.
    """
    # Get theme specific assets
    try:
        main_menu_background, options_menu_background, game_board_background = get_theme_specific_assets(theme)
    except (pygame.error, FileNotFoundError) as e:
        logger.error(f"Failed to load theme asset: {e}")
        return None

    # Get common assets
    try:
        common_assets: CommonAssets = get_common_assets()
    except (pygame.error, FileNotFoundError) as e:
        logger.error(f"Failed to load common asset: {e}")
        return None

    active_backgrounds = BackgroundContainer(
        main_menu=main_menu_background,
        options_menu=options_menu_background,
        game_board=game_board_background,
        credits=common_assets["credits"]
    )

    return AssetsContainer(
        backgrounds=active_backgrounds,
        buttons=common_assets["button_assets"],
        discs=common_assets["disc_assets"],
        setting_indicators=common_assets["setting_indicator_assets"],
        game_notifications=common_assets["notification_assets"],
        tutorial_images=common_assets["tutorial_assets"]
    )
