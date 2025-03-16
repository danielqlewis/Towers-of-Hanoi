from dataclasses import dataclass
import pygame
from typing import Dict, Tuple, TypedDict
from constants import MenuTheme, ButtonFlag


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
        main_menu = pygame.image.load("assets/red/Menu_BG.png").convert()
        options_menu = pygame.image.load("assets/red/Options_BG.png").convert()
        game_board = pygame.image.load("assets/red/Game_BG.png").convert()
    elif theme == MenuTheme.BLUE:
        main_menu = pygame.image.load("assets/blue/Menu_BG.png").convert()
        options_menu = pygame.image.load("assets/blue/Options_BG.png").convert()
        game_board = pygame.image.load("assets/blue/Game_BG.png").convert()
    else:
        main_menu = pygame.image.load("assets/default/Menu_BG.png").convert()
        options_menu = pygame.image.load("assets/default/Options_BG.png").convert()
        game_board = pygame.image.load("assets/default/Game_BG.png").convert()

    return main_menu, options_menu, game_board


def get_common_assets() -> CommonAssets:
    credits_background = pygame.image.load("assets/Credit_Page.png").convert()

    # Buttons###########################################################################################################
    standard_buttons = {ButtonFlag.PLAY: pygame.image.load("assets/Play_Button_Base.png").convert(),
                        ButtonFlag.OPTIONS: pygame.image.load("assets/Options_Button_Base.png").convert(),
                        ButtonFlag.EXIT: pygame.image.load("assets/Exit_Button_Base.png").convert(),
                        ButtonFlag.TUTORIAL: pygame.image.load("assets/Tutorial_Button_Base.png").convert(),
                        ButtonFlag.CREDITS: pygame.image.load("assets/Credits_Button_Base.png").convert(),
                        ButtonFlag.DIFFICULTY_TOGGLE: pygame.image.load("assets/Difficulty_Button_Base.png").convert(),
                        ButtonFlag.RESOLUTION_TOGGLE: pygame.image.load("assets/Resolution_Button_Base.png").convert(),
                        ButtonFlag.THEME_TOGGLE: pygame.image.load("assets/Style_Button_Base.png").convert(),
                        ButtonFlag.BACK_TO_MAIN: pygame.image.load("assets/Back_Button_Base.png").convert(),
                        ButtonFlag.ACCEPT_SETTINGS: pygame.image.load("assets/Accept_Button_Base.png").convert(),
                        ButtonFlag.RESET_BOARD: pygame.image.load("assets/Refresh_Button_Base.png").convert()}

    highlighted_buttons = {ButtonFlag.PLAY: pygame.image.load("assets/Play_Button_Selected.png").convert(),
                           ButtonFlag.OPTIONS: pygame.image.load("assets/Options_Button_Selected.png").convert(),
                           ButtonFlag.EXIT: pygame.image.load("assets/Exit_Button_Selected.png").convert(),
                           ButtonFlag.TUTORIAL: pygame.image.load("assets/Tutorial_Button_Selected.png").convert(),
                           ButtonFlag.CREDITS: pygame.image.load("assets/Credits_Button_Selected.png").convert(),
                           ButtonFlag.DIFFICULTY_TOGGLE: pygame.image.load(
                               "assets/Difficulty_Button_Selected.png").convert(),
                           ButtonFlag.RESOLUTION_TOGGLE: pygame.image.load(
                               "assets/Resolution_Button_Selected.png").convert(),
                           ButtonFlag.THEME_TOGGLE: pygame.image.load("assets/Style_Button_Selected.png").convert(),
                           ButtonFlag.BACK_TO_MAIN: pygame.image.load("assets/Back_Button_Selected.png").convert(),
                           ButtonFlag.ACCEPT_SETTINGS: pygame.image.load("assets/Accept_Button_Selected.png").convert(),
                           ButtonFlag.RESET_BOARD: pygame.image.load("assets/Refresh_Button_Selected.png").convert()}

    local_buttons = ButtonContainer(standard=standard_buttons, highlighted=highlighted_buttons)

    # Discs#############################################################################################################
    standard_discs = {0: pygame.image.load("assets/Plate_0_b.png").convert(),
                      1: pygame.image.load("assets/Plate_1_b.png").convert(),
                      2: pygame.image.load("assets/Plate_2_b.png").convert(),
                      3: pygame.image.load("assets/Plate_3_b.png").convert(),
                      4: pygame.image.load("assets/Plate_4_b.png").convert()}

    highlighted_discs = {0: pygame.image.load("assets/Plate_0_s.png").convert(),
                         1: pygame.image.load("assets/Plate_1_s.png").convert(),
                         2: pygame.image.load("assets/Plate_2_s.png").convert(),
                         3: pygame.image.load("assets/Plate_3_s.png").convert(),
                         4: pygame.image.load("assets/Plate_4_s.png").convert()}

    local_discs = DiscContainer(standard=standard_discs, highlighted=highlighted_discs)

    # Indicators########################################################################################################
    difficulty_indicators = {3: pygame.image.load("assets/Difficulty_Display_1.png").convert(),
                             4: pygame.image.load("assets/Difficulty_Display_2.png").convert(),
                             5: pygame.image.load("assets/Difficulty_Display_3.png").convert()}

    resolution_indicators = {(720, 480): pygame.image.load("assets/Resolution_Display_1.png").convert(),
                             (864, 576): pygame.image.load("assets/Resolution_Display_2.png").convert(),
                             (960, 640): pygame.image.load("assets/Resolution_Display_3.png").convert(),
                             (1080, 720): pygame.image.load("assets/Resolution_Display_4.png").convert(),
                             (1296, 864): pygame.image.load("assets/Resolution_Display_5.png").convert()}

    theme_indicators = {MenuTheme.STANDARD: pygame.image.load("assets/Style_Display_1.png").convert(),
                        MenuTheme.RED: pygame.image.load("assets/Style_Display_2.png").convert(),
                        MenuTheme.BLUE: pygame.image.load("assets/Style_Display_3.png").convert()}

    local_setting_indicators = SettingIndicatorContainer(difficulty=difficulty_indicators,
                                                         resolution=resolution_indicators,
                                                         theme=theme_indicators)

    # Notifications#####################################################################################################
    illegal_move_image = pygame.image.load("assets/Big_X.png").convert_alpha()
    victory_image = pygame.image.load("assets/Victory.png").convert_alpha()
    local_notificatons = GameNotificationContainer(illegal_move=illegal_move_image, victory=victory_image)

    # Tutorial##########################################################################################################
    tutorial_slides = {0: pygame.image.load("assets/Tutorial_1.png").convert(),
                       1: pygame.image.load("assets/Tutorial_2.png").convert(),
                       2: pygame.image.load("assets/Tutorial_3.png").convert(),
                       3: pygame.image.load("assets/Tutorial_4.png").convert(),
                       4: pygame.image.load("assets/Tutorial_5.png").convert(),
                       5: pygame.image.load("assets/Tutorial_6.png").convert(),
                       6: pygame.image.load("assets/Tutorial_7.png").convert(),
                       7: pygame.image.load("assets/Tutorial_8.png").convert()}

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
