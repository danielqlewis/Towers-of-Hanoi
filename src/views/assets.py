from dataclasses import dataclass
import pygame
from typing import Dict, Tuple, TypedDict
from src.constants import MenuTheme, ButtonFlag
from src.utils.asset_loader import load_image, load_image_with_alpha


@dataclass(frozen=True)
class BackgroundContainer:
    main_menu: pygame.Surface
    options_menu: pygame.Surface
    game_board: pygame.Surface
    credits: pygame.Surface


@dataclass(frozen=True)
class ButtonContainer:
    standard: Dict[ButtonFlag, pygame.Surface]
    highlighted: Dict[ButtonFlag, pygame.Surface]


@dataclass(frozen=True)
class DiscContainer:
    standard: Dict[int, pygame.Surface]
    highlighted: Dict[int, pygame.Surface]


@dataclass(frozen=True)
class SettingIndicatorContainer:
    difficulty: Dict[int, pygame.Surface]
    resolution: Dict[Tuple, pygame.Surface]
    theme: Dict[MenuTheme, pygame.Surface]


@dataclass(frozen=True)
class GameNotificationContainer:
    illegal_move: pygame.Surface
    victory: pygame.Surface


@dataclass(frozen=True)
class TutorialSlidesContainer:
    slides: Dict[int, pygame.Surface]


@dataclass(frozen=True)
class AssetsContainer:
    backgrounds: BackgroundContainer
    buttons: ButtonContainer
    discs: DiscContainer
    setting_indicators: SettingIndicatorContainer
    game_notifications: GameNotificationContainer
    tutorial_images: TutorialSlidesContainer


class CommonAssets(TypedDict):
    credits: pygame.Surface
    button_assets: ButtonContainer
    disk_assets: DiscContainer
    setting_indicator_assets: SettingIndicatorContainer
    notification_assets: GameNotificationContainer
    tutorial_assets: TutorialSlidesContainer


def get_theme_specific_assets(theme: MenuTheme) -> Tuple[pygame.Surface, pygame.Surface, pygame.Surface]:
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
    credits_background = load_image("Credit_Page.png")

    # Buttons###########################################################################################################
    standard_buttons = {ButtonFlag.PLAY: load_image("Play_Button_Base.png"),
                        ButtonFlag.OPTIONS: load_image("Options_Button_Base.png"),
                        ButtonFlag.EXIT: load_image("Exit_Button_Base.png"),
                        ButtonFlag.TUTORIAL: load_image("Tutorial_Button_Base.png"),
                        ButtonFlag.CREDITS: load_image("Credits_Button_Base.png"),
                        ButtonFlag.DIFFICULTY_TOGGLE: load_image("Difficulty_Button_Base.png"),
                        ButtonFlag.RESOLUTION_TOGGLE: load_image("Resolution_Button_Base.png"),
                        ButtonFlag.THEME_TOGGLE: load_image("Style_Button_Base.png"),
                        ButtonFlag.BACK_TO_MAIN: load_image("Back_Button_Base.png"),
                        ButtonFlag.ACCEPT_SETTINGS: load_image("Accept_Button_Base.png"),
                        ButtonFlag.RESET_BOARD: load_image("Refresh_Button_Base.png")}

    highlighted_buttons = {ButtonFlag.PLAY: load_image("Play_Button_Selected.png"),
                           ButtonFlag.OPTIONS: load_image("Options_Button_Selected.png"),
                           ButtonFlag.EXIT: load_image("Exit_Button_Selected.png"),
                           ButtonFlag.TUTORIAL: load_image("Tutorial_Button_Selected.png"),
                           ButtonFlag.CREDITS: load_image("Credits_Button_Selected.png"),
                           ButtonFlag.DIFFICULTY_TOGGLE: load_image("Difficulty_Button_Selected.png"),
                           ButtonFlag.RESOLUTION_TOGGLE: load_image("Resolution_Button_Selected.png"),
                           ButtonFlag.THEME_TOGGLE: load_image("Style_Button_Selected.png"),
                           ButtonFlag.BACK_TO_MAIN: load_image("Back_Button_Selected.png"),
                           ButtonFlag.ACCEPT_SETTINGS: load_image("Accept_Button_Selected.png"),
                           ButtonFlag.RESET_BOARD: load_image("Refresh_Button_Selected.png")}

    local_buttons = ButtonContainer(standard=standard_buttons, highlighted=highlighted_buttons)

    # Discs#############################################################################################################
    standard_discs = {0: load_image("Plate_0_b.png"),
                      1: load_image("Plate_1_b.png"),
                      2: load_image("Plate_2_b.png"),
                      3: load_image("Plate_3_b.png"),
                      4: load_image("Plate_4_b.png")}

    highlighted_discs = {0: load_image("Plate_0_s.png"),
                         1: load_image("Plate_1_s.png"),
                         2: load_image("Plate_2_s.png"),
                         3: load_image("Plate_3_s.png"),
                         4: load_image("Plate_4_s.png")}

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
    tutorial_slides = {0: load_image("Tutorial_1.png"),
                       1: load_image("Tutorial_2.png"),
                       2: load_image("Tutorial_3.png"),
                       3: load_image("Tutorial_4.png"),
                       4: load_image("Tutorial_5.png"),
                       5: load_image("Tutorial_6.png"),
                       6: load_image("Tutorial_7.png"),
                       7: load_image("Tutorial_8.png")}

    local_tutorials = TutorialSlidesContainer(slides=tutorial_slides)

    return {
        "credits": credits_background,
        "button_assets": local_buttons,
        "disk_assets": local_discs,
        "setting_indicator_assets": local_setting_indicators,
        "notification_assets": local_notificatons,
        "tutorial_assets": local_tutorials
    }


def build_asset_container(theme: MenuTheme) -> AssetsContainer:
    # Get theme specific assets
    try:
        main_menu_background, options_menu_background, game_board_background = get_theme_specific_assets(theme)
    except (pygame.error, FileNotFoundError) as e:
        print(f"Failed to load theme asset: {e}")
        return None

    # Get common assets
    try:
        common_assets: CommonAssets = get_common_assets()
    except (pygame.error, FileNotFoundError) as e:
        print(f"Failed to load common asset: {e}")
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
        discs=common_assets["disk_assets"],
        setting_indicators=common_assets["setting_indicator_assets"],
        game_notifications=common_assets["notification_assets"],
        tutorial_images=common_assets["tutorial_assets"]
    )
