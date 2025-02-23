# File: Tower_of_Hanoi.py
# Purpose: Implementation of the Tower of Hanoi game
# Author: Daniel Lewis
# Date: April 21, 2023
# Dependencies: Pygame
# Version history:
# - 1.0: Initial version
# Contact: omega0800@gmail.com

# Imports
import sys
import pygame
from pygame.locals import *
from typing import Tuple, List, Optional
from enum import Enum
from collections import namedtuple
from collections import defaultdict

# Global settings variable to store game settings

TOWER_OF_HANOI_SETTINGS = namedtuple('TOWER_OF_HANOI_SETTINGS', ['screen_size', 'difficulty', 'visual_style'])
settings = TOWER_OF_HANOI_SETTINGS(screen_size=2, difficulty=0, visual_style=0)


# Enums for game states, button flags, and what type of information is being displayed.

class GameState(Enum):
    MENU = 1
    GAMEPLAY = 2
    INFO_DISPLAY = 3


class ButtonFlag(Enum):
    PLAY = "PLAY"
    OPTIONS = "OPTIONS"
    EXIT = "EXIT"
    CREDITS = "CREDITS"
    REFRESH = "REFRESH"
    BACK = "BACK"
    TUTORIAL = "TUTORIAL"
    TOGGLE_DIFFICULTY = "TOGGLE_DIFFICULTY"
    TOGGLE_RESOLUTION = "TOGGLE_RESOLUTION"
    TOGGLE_STYLE = "TOGGLE_STYLE"
    ACCEPT = "ACCEPT"


class InfoType(Enum):
    TUTORIAL_1 = 1
    TUTORIAL_2 = 2
    TUTORIAL_3 = 3
    TUTORIAL_4 = 4
    TUTORIAL_5 = 5
    TUTORIAL_6 = 6
    TUTORIAL_7 = 7
    TUTORIAL_8 = 8
    ILLEGAL_MOVE = 9
    VICTORY = 10
    CREDITS = 11


# Program specific sprite classes

class NotificationSprite(pygame.sprite.DirtySprite):
    def __init__(self, image: pygame.Surface, location: Tuple[int, int]) -> None:
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(midtop=location)
        self.dirty = 0


class Button(pygame.sprite.DirtySprite):
    def __init__(self, image_set: List[pygame.Surface], pos: Tuple[int, int], flag: ButtonFlag) -> None:
        super().__init__()
        self.image_set = image_set
        self.image = self.image_set[0]
        self.rect = self.image.get_rect(center=pos)
        self.hovered = False
        self.flag = flag
        self.clicked = False

    def update(self, mouse_pos: Tuple[int, int], mouse_clicked: bool) -> None:
        prev_hovered = self.hovered
        self.hovered = self.rect.collidepoint(mouse_pos)

        if self.hovered != prev_hovered:
            self.dirty = 1
            # Alternates between the first and second image in the image set,
            # depending on the current image of the button
            self.image = self.image_set[1] if self.image == self.image_set[0] else self.image_set[0]

        if self.hovered and mouse_clicked:
            self.clicked = True

    def handle_click(self) -> None:
        self.clicked = False
        self.hovered = False
        self.image = self.image_set[0]


class Plate(pygame.sprite.DirtySprite):
    # Class-level constants
    PLATE_BASE_WIDTH = 86
    PLATE_SIZE_WIDTH_MULTIPLIER = 43
    PLATE_HEIGHT = 71
    PEG_CENTERX = [192, 480, 768]
    PLATE_BOTTOM = 587
    PLATE_HEIGHT_MULTIPLIER = 69

    def __init__(self, size: int, height: int, image_sets: List[List[pygame.Surface]]) -> None:
        super().__init__()
        self.size = size
        self.height = height
        self.peg = 0
        self.selected = False
        self.base_image = image_sets[0][self.size]
        self.select_image = image_sets[1][self.size]
        self.image = self.base_image
        self.rect = pygame.Rect(0, 0, Plate.PLATE_BASE_WIDTH + (Plate.PLATE_SIZE_WIDTH_MULTIPLIER * self.size),
                                Plate.PLATE_HEIGHT)
        self.rect.centerx = Plate.PEG_CENTERX[self.peg]
        self.rect.bottom = Plate.PLATE_BOTTOM - (Plate.PLATE_HEIGHT_MULTIPLIER * self.height)
        self.dirty = 1

    def change_selection_state(self) -> None:
        self.selected = not self.selected
        if self.selected:
            self.image = self.select_image
        else:
            self.image = self.base_image
        self.dirty = 1

    def update_position(self, target_peg: int, new_height: int) -> None:
        # Update the peg and height attributes
        self.peg = target_peg
        self.height = new_height
        # Update the rect attributes for the new position on the screen
        self.rect.centerx = Plate.PEG_CENTERX[self.peg]
        self.rect.bottom = Plate.PLATE_BOTTOM - (Plate.PLATE_HEIGHT_MULTIPLIER * self.height)
        # Call the change_selection_state method to update the image and dirty flag
        self.change_selection_state()


# Information Container Classes

class ProgramState:
    def __init__(self) -> None:
        self.game_state = GameState.MENU
        self.dirty = True
        self.running = True
        self.info_type = None
        self.setup_needed = True
        self.setting_changed_flags = [False, False]
        self.program_return_value = 0

    def resolve_illegalmove(self) -> None:
        self.game_state = GameState.INFO_DISPLAY
        self.info_type = InfoType.ILLEGAL_MOVE
        self.setup_needed = True

    def handle_error(self, error_string: str, error_object):
        print(f"{error_string:}: {error_object}")
        self.program_return_value = 1
        self.running = False


class AssetInformation:
    def __init__(self):
        self.active_sprites = pygame.sprite.LayeredDirty()
        self.background_image = None
        self.active_buttons = None

    def resolve_sprite_setup(self, new_buttons, new_sprites=None):
        self.active_buttons = new_buttons
        self.active_sprites.empty()
        self.active_sprites.add(new_buttons)
        if new_sprites is not None:
            self.active_sprites.add(new_sprites)

    def resolve_background_setup(self, new_background_sprite):
        self.active_sprites.add(new_background_sprite)
        self.background_image = new_background_sprite.image


# Image & Sprite Loading

class ImageLoader:
    def __init__(self) -> None:
        self.background_dict: Dict[str, pygame.Surface] = {}
        self.plate_image_sets: List[Dict[int, pygame.Surface]] = []
        self.button_pair_dict = defaultdict(list)
        self.notification_dict: Dict[str, pygame.Surface] = {}
        self.tutorial_dict: Dict[str, pygame.Surface] = {}

    def load_images(self, style: str = 'default', program_state: Optional[ProgramState] = None) -> None:
        path_prefix = self._get_path_prefix(style)

        try:
            self._load_background_images(path_prefix)
        except pygame.error as e:
            program_state.handle_error("Error loading background images", e)

        try:
            self._load_plate_images()
        except pygame.error as e:
            program_state.handle_error("Error loading plate images", e)

        try:
            self._load_button_images()
        except pygame.error as e:
            program_state.handle_error("Error loading button images", e)

        try:
            self._load_notification_images()
        except pygame.error as e:
            program_state.handle_error("Error loading notification images", e)

        try:
            self._load_tutorial_images()
        except pygame.error as e:
            program_state.handle_error("Error loading tutorial images", e)

    def _get_path_prefix(self, style: str) -> str:
        # Placeholder method to determine path prefix based on image style
        if style == 'blue':
            return 'Assets/blue/'
        elif style == 'red':
            return 'Assets/red/'
        else:
            return 'Assets/default/'

    def _load_background_images(self, path_prefix: str) -> None:
        self.background_dict['menu'] = pygame.image.load(path_prefix + 'Menu_BG.png')
        self.background_dict['game'] = pygame.image.load(path_prefix + 'Game_BG.png')
        self.background_dict['options'] = pygame.image.load(path_prefix + 'Options_BG.png')

    def _load_plate_images(self) -> None:
        base_plate_images_dict = {}
        selected_plate_images_dict = {}
        for i in range(5):
            base_plate_images_dict[i] = pygame.image.load(f"Assets/Plate_{i}_b.png")
            selected_plate_images_dict[i] = pygame.image.load(f"Assets/Plate_{i}_s.png")
        self.plate_image_sets = [base_plate_images_dict, selected_plate_images_dict]

    def _load_button_images(self) -> None:
        button_set = ['Play', 'Options', 'Exit', 'Credits', 'Tutorial', 'Back', 'Refresh', 'Accept', 'Difficulty',
                      'Resolution', 'Style']
        for name in button_set:
            base_button_image = pygame.image.load(f"Assets/{name}_Button_Base.png")
            selected_button_image = pygame.image.load(f"Assets/{name}_Button_Selected.png")
            self.button_pair_dict[name] = [base_button_image, selected_button_image]

    def _load_notification_images(self) -> None:
        single_images = {
            'illegal move': 'Big_X.png',
            'victory': 'Victory.png',
            'credits': 'Credit_Page.png'
        }

        image_sets = {
            'difficulty': ['Difficulty_Display_1.png', 'Difficulty_Display_2.png', 'Difficulty_Display_3.png'],
            'resolution': ['Resolution_Display_1.png', 'Resolution_Display_2.png', 'Resolution_Display_3.png',
                           'Resolution_Display_4.png', 'Resolution_Display_5.png'],
            'style': ['Style_Display_1.png', 'Style_Display_2.png', 'Style_Display_3.png']
        }

        for key, value in single_images.items():
            self.notification_dict[key] = pygame.image.load(f"Assets/{value}")

        for key, value in image_sets.items():
            for i, item in enumerate(value):
                self.notification_dict[f'{key}_{i}'] = pygame.image.load(f"Assets/{item}")

    def _load_tutorial_images(self) -> None:
        for i in range(8):
            self.notification_dict[f'step_{i}'] = pygame.image.load(f"Assets/Tutorial_{i + 1}.png")


class SpriteLoader:
    # Class-level constants
    BackgroundSprites = namedtuple('BackgroundSprites', ['main_menu', 'options_menu', 'game'])
    ButtonGroups = namedtuple('ButtonGroups', ['main_menu', 'options_menu', 'game'])
    NotificationSprites = namedtuple('NotificationSprites', ['credits', 'illegal_move', 'victory', 'difficulties',
                                                             'resolutions', 'styles', 'tutorials'])
    flag_dict = {'Play': ButtonFlag.PLAY, 'Options': ButtonFlag.OPTIONS, 'Exit': ButtonFlag.EXIT,
                 'Tutorial': ButtonFlag.TUTORIAL, 'Credits': ButtonFlag.CREDITS,
                 'Difficulty': ButtonFlag.TOGGLE_DIFFICULTY, 'Resolution': ButtonFlag.TOGGLE_RESOLUTION,
                 'Style': ButtonFlag.TOGGLE_STYLE, 'Back': ButtonFlag.BACK, 'Accept': ButtonFlag.ACCEPT,
                 'Refresh': ButtonFlag.REFRESH}

    def __init__(self, image_loader: ImageLoader) -> None:
        self.image_loader = image_loader
        self.background_sprites = self.create_background_sprites()
        self.program_buttons = self.create_button_groups()
        self.notification_sprites = self.create_notification_sprites()

    def create_background_sprites(self):
        bg_names = ['menu', 'options', 'game']
        backgrounds = [pygame.sprite.DirtySprite() for _ in bg_names]
        for name, bg_sprite in zip(bg_names, backgrounds):
            bg_sprite.image = self.image_loader.background_dict[name]
            bg_sprite.rect = pygame.Rect(0, 0, 960, 640)

        return SpriteLoader.BackgroundSprites(*backgrounds)

    def create_single_button_group(self, button_set_info: List[Tuple[str, Tuple[int, int]]]) -> List[Button]:
        report = []
        for button_info in button_set_info:
            button_image = self.image_loader.button_pair_dict[button_info[0]]
            new_button = Button(button_image, button_info[1], SpriteLoader.flag_dict[button_info[0]])
            report.append(new_button)
        return report

    def create_button_groups(self):

        main_menu_buttons_info = [['Play', (480, 300)], ['Options', (480, 400)], ['Exit', (480, 500)],
                                  ['Tutorial', (140, 570)], ['Credits', (820, 570)]]

        options_menu_buttons_info = [['Difficulty', (400, 220)], ['Resolution', (400, 340)], ['Style', (400, 440)],
                                     ['Back', (70, 70)], ['Accept', (480, 560)]]

        gameplay_buttons_info = [['Back', (60, 60)], ['Refresh', (900, 60)]]

        main_menu_buttons = self.create_single_button_group(main_menu_buttons_info)
        options_buttons = self.create_single_button_group(options_menu_buttons_info)
        game_buttons = self.create_single_button_group(gameplay_buttons_info)

        return SpriteLoader.ButtonGroups(main_menu=main_menu_buttons, options_menu=options_buttons, game=game_buttons)

    def create_notifications_subset(self, set_size: int, keystring: str, position: Tuple[int, int]) -> List[
                                                                                                    NotificationSprite]:
        report = []
        for i in range(set_size):
            notification_image = self.image_loader.notification_dict[f'{keystring}_{i}']
            new_notification = NotificationSprite(notification_image, position)
            report.append(new_notification)
        return report

    def create_notification_sprites(self):
        notification_image_dict = self.image_loader.notification_dict

        credits_notification = NotificationSprite(notification_image_dict['credits'], [480, 0])
        illegalmove_notification = NotificationSprite(notification_image_dict['illegal move'], [480, 20])
        victory_notificiation = NotificationSprite(notification_image_dict['victory'], [480, 160])

        difficulty_notifs_info = [3, 'difficulty', [600, 160]]
        resolution_notifs_info = [5, 'resolution', [690, 300]]
        style_notifs_info = [3, 'style', [640, 400]]
        tutorial_notifs_info = [8, 'step', [480, 0]]

        difficulty_notifications = self.create_notifications_subset(*difficulty_notifs_info)
        resolution_notifications = self.create_notifications_subset(*resolution_notifs_info)
        style_notifications = self.create_notifications_subset(*style_notifs_info)
        tutorial_notifications = self.create_notifications_subset(*tutorial_notifs_info)

        return SpriteLoader.NotificationSprites(credits=credits_notification, illegal_move=illegalmove_notification,
                                                victory=victory_notificiation, difficulties=difficulty_notifications,
                                                resolutions=resolution_notifications, styles=style_notifications,
                                                tutorials=tutorial_notifications)


# Auxiliary Classes

class GameBoard:
    # Class-level constants
    PLAY_AREA_RECT = [48, 160, 864, 426]

    def __init__(self, plate_images: List[List[pygame.Surface]], plate_set_size: int = 3) -> None:
        # Create the initial plate set with decreasing sizes and increasing hights
        self.plate_set = [Plate(plate_set_size - x - 1, x, plate_images) for x in range(plate_set_size)]
        self.selected_plate = None
        self.play_rect = pygame.Rect(GameBoard.PLAY_AREA_RECT)
        third_width = self.play_rect.width // 3
        self.left_third = self.play_rect.left + third_width
        self.right_third = self.left_third + third_width

    def click_check(self, click_point: Tuple[int, int]) -> Optional[int]:
        report = None
        if self.play_rect.collidepoint(*click_point):
            if click_point[0] < self.left_third:
                report = 0
            elif click_point[0] > self.right_third:
                report = 2
            else:
                report = 1
        return report

    def topplate_check(self) -> bool:
        for plate in self.plate_set:
            if plate.peg == self.selected_plate.peg:
                if plate.height > self.selected_plate.height:
                    return False
        return True

    def target_check(self, target: int) -> bool:
        peg_contents = [x for x in self.plate_set if x.peg == target]
        if peg_contents:
            topmost_plate = max(peg_contents, key=lambda obj: obj.height)
            if topmost_plate.size < self.selected_plate.size:
                return False
        return True

    def move_legal_check(self, target: int) -> bool:
        report = self.topplate_check()
        if report:
            report = self.target_check(target)
        return report

    def victory_check(self) -> bool:
        report = True
        for plate in self.plate_set:
            if plate.peg < 2:
                report = False
                break
        return report


class TempSettings:
    def __init__(self, display_sprites: SpriteLoader.NotificationSprites) -> None:
        self.difficulty_sprites = display_sprites.difficulties
        self.resolution_sprites = display_sprites.resolutions
        self.style_sprites = display_sprites.styles
        self.difficulty = settings.difficulty
        self.visual_style = settings.visual_style
        self.screen_size = settings.screen_size

    def update(self, setting: str) -> None:
        # Cycle through 3, 5, and 3 options respectively
        if setting == 'difficulty':
            self.difficulty = (self.difficulty + 1) % 3
        elif setting == 'screen_size':
            self.screen_size = (self.screen_size + 1) % 5
        elif setting == 'visual_style':
            self.visual_style = (self.visual_style + 1) % 3


# Handler Classes

class ButtonHandler:
    def __init__(self):
        self.menu_state = 'main'
        self.temp_settings = None

    def menu_setup(self, program_state: ProgramState, asset_information: AssetInformation,
                   sprite_loader: SpriteLoader) -> None:

        if self.menu_state == 'main':
            if program_state.setting_changed_flags[0]:
                style_flag = ['default', 'red', 'blue'][settings.visual_style]
                sprite_loader.image_loader.load_images(style=style_flag,
                                                       program_state=program_state)  # specify parameter names
                sprite_loader.background_sprites = sprite_loader.create_background_sprites()

            program_state.setting_changed_flags = [False, False]

            button_set = sprite_loader.program_buttons.main_menu
            sprite_set = []
            background_sprite = sprite_loader.background_sprites.main_menu

        else:
            # create instance of TempSettings to hold options user is considering
            self.temp_settings = TempSettings(sprite_loader.notification_sprites)

            button_set = sprite_loader.program_buttons.options_menu
            sprite_set = [sprite_loader.notification_sprites.difficulties[settings.difficulty],
                          sprite_loader.notification_sprites.resolutions[settings.screen_size],
                          sprite_loader.notification_sprites.styles[settings.visual_style]]
            background_sprite = sprite_loader.background_sprites.options_menu

        asset_information.resolve_background_setup(background_sprite)
        asset_information.resolve_sprite_setup(button_set, sprite_set)

    def handle_setting_change(self, program_state: ProgramState) -> None:
        global settings
        # If the visual style changed, flag it.
        if settings.visual_style != self.temp_settings.visual_style:
            program_state.setting_changed_flags[0] = True
        # If the screen size changed, flag it.
        if settings.screen_size != self.temp_settings.screen_size:
            program_state.setting_changed_flags[1] = True
        self.menu_state = 'main'
        program_state.setup_needed = True
        # Implement changed settings
        settings = TOWER_OF_HANOI_SETTINGS(screen_size=self.temp_settings.screen_size,
                                           difficulty=self.temp_settings.difficulty,
                                           visual_style=self.temp_settings.visual_style)

    def handle_toggle_buttons(self, asset_information: AssetInformation, button: Button) -> None:
        toggle_map = {
            ButtonFlag.TOGGLE_DIFFICULTY: ('difficulty', 'difficulty_sprites'),
            ButtonFlag.TOGGLE_RESOLUTION: ('screen_size', 'resolution_sprites'),
            ButtonFlag.TOGGLE_STYLE: ('visual_style', 'style_sprites')
        }

        # determine which setting was toggled
        attr, sprites_attr = toggle_map[button.flag]

        # remove sprite for old selection
        current_value = getattr(self.temp_settings, attr)
        current_sprites = getattr(self.temp_settings, sprites_attr)
        asset_information.active_sprites.remove(current_sprites[current_value])

        # update the settings value
        self.temp_settings.update(attr)

        # add sprite for new selection
        new_value = getattr(self.temp_settings, attr)
        asset_information.active_sprites.add(current_sprites[new_value])

    def handle_general_button(self, program_state: ProgramState, button: Button) -> None:
        if button.flag == ButtonFlag.EXIT:
            program_state.running = False
        else:
            if button.flag == ButtonFlag.PLAY:
                program_state.game_state = GameState.GAMEPLAY
            elif button.flag == ButtonFlag.OPTIONS:
                self.menu_state = 'options'
            elif button.flag == ButtonFlag.BACK:
                program_state.game_state = GameState.MENU
                self.menu_state = 'main'
            elif button.flag == ButtonFlag.CREDITS:
                program_state.game_state = GameState.INFO_DISPLAY
                program_state.info_type = InfoType.CREDITS
            elif button.flag == ButtonFlag.TUTORIAL:
                program_state.game_state = GameState.INFO_DISPLAY
                program_state.info_type = InfoType.TUTORIAL_1
            program_state.setup_needed = True

    def button_frame(self, program_state: ProgramState, asset_information: AssetInformation,
                     mouse_event: namedtuple) -> None:

        for button in asset_information.active_buttons:
            button.update(mouse_event.pos, mouse_event.clicked)
            # handle hover/unhover
            if button.dirty and not program_state.dirty:
                program_state.dirty = True

            # handle click
            if button.clicked:
                button.handle_click()
                if button.flag == ButtonFlag.ACCEPT:
                    self.handle_setting_change(program_state)
                elif "TOGGLE" in button.flag.value:
                    self.handle_toggle_buttons(asset_information, button)
                else:
                    self.handle_general_button(program_state, button)
                break


class GamePlayHandler:
    def __init__(self):
        self.game_board = None

    def gameplay_setup(self, asset_information: AssetInformation, sprite_loader: SpriteLoader) -> None:
        # Set up the game board with plate image sets and difficulty level
        self.game_board = GameBoard(sprite_loader.image_loader.plate_image_sets, settings.difficulty + 3)

        # Resolve background and sprite setup using asset_information and sprite_loader
        button_set = sprite_loader.program_buttons.game
        sprite_set = self.game_board.plate_set
        background_sprite = sprite_loader.background_sprites.game

        asset_information.resolve_background_setup(background_sprite)
        asset_information.resolve_sprite_setup(button_set, sprite_set)

    def gameplay_handle_victorycheck(self, program_state: ProgramState) -> None:
        if self.game_board.victory_check():
            program_state.game_state = GameState.INFO_DISPLAY
            program_state.info_type = InfoType.VICTORY
            program_state.setup_needed = True

    def gameplay_handle_selectplate(self, program_state: ProgramState, mouse_event: namedtuple) -> None:
        for plate in self.game_board.plate_set:
            if plate.rect.collidepoint(mouse_event.pos):
                self.game_board.selected_plate = plate
                plate.change_selection_state()
                program_state.dirty = True
                break

    def gameplay_handle_deselectplate(self, program_state: ProgramState) -> None:
        self.game_board.selected_plate.change_selection_state()
        self.game_board.selected_plate = None
        program_state.dirty = True

    def gameplay_handle_attemptedmove(self, program_state: ProgramState, target_peg: Optional[int]) -> bool:
        plate_moved = False
        if target_peg is not None:
            if target_peg != self.game_board.selected_plate.peg:
                if self.game_board.move_legal_check(target_peg):
                    plate_moved = True
                    new_height = len([x for x in self.game_board.plate_set if x.peg == target_peg])
                    self.game_board.selected_plate.update_position(target_peg, new_height)
                    self.game_board.selected_plate = None
                    program_state.dirty = True
                else:
                    program_state.resolve_illegalmove()
        return plate_moved

    def gameplay_frame(self, program_state: ProgramState, mouse_event: namedtuple):
        if mouse_event.clicked:
            if self.game_board.selected_plate:
                if self.game_board.selected_plate.rect.collidepoint(mouse_event.pos):
                    self.gameplay_handle_deselectplate(program_state)
                else:
                    target_peg = self.game_board.click_check(mouse_event.pos)
                    plate_moved = self.gameplay_handle_attemptedmove(program_state, target_peg)
                    if plate_moved:
                        self.gameplay_handle_victorycheck(program_state)
            else:
                self.gameplay_handle_selectplate(program_state, mouse_event)


class NotificationHandler:
    def __init__(self):
        self.info_buffer = 0

    def notification_setup(self, program_state: ProgramState, asset_information: AssetInformation,
                           sprite_loader: SpriteLoader) -> None:
        self.info_buffer = 40
        if program_state.info_type == InfoType.CREDITS:
            asset_information.active_sprites.add(sprite_loader.notification_sprites.credits)
        elif program_state.info_type == InfoType.ILLEGAL_MOVE:
            asset_information.active_sprites.add(sprite_loader.notification_sprites.illegal_move)
        elif program_state.info_type == InfoType.VICTORY:
            asset_information.active_sprites.add(sprite_loader.notification_sprites.victory)
        else:
            tutorial_index = program_state.info_type.value - InfoType.TUTORIAL_1.value
            active_tutorial_notification = sprite_loader.notification_sprites.tutorials[tutorial_index]
            asset_information.active_sprites.add(active_tutorial_notification)

    def notification_frame(self, program_state: ProgramState, asset_information: AssetInformation,
                           mouse_clicked: bool) -> None:
        if self.info_buffer > 0:
            self.info_buffer -= 1
        else:
            if mouse_clicked:
                self.info_buffer = 0
                if program_state.info_type == InfoType.ILLEGAL_MOVE:
                    program_state.game_state = GameState.GAMEPLAY
                    for sprite in asset_information.active_sprites:
                        if type(sprite) == NotificationSprite:
                            asset_information.active_sprites.remove(sprite)
                    program_state.dirty = True
                else:
                    program_state.setup_needed = True
                    if program_state.info_type in [InfoType.VICTORY, InfoType.CREDITS, InfoType.TUTORIAL_8]:
                        program_state.game_state = GameState.MENU
                    else:
                        current_tutorial = program_state.info_type.value
                        next_tutorial = current_tutorial + 1
                        next_tutorial_name = f"TUTORIAL_{next_tutorial}"
                        program_state.info_type = InfoType[next_tutorial_name]


# Manager Class

class HandlerManager:
    def __init__(self, program_state):
        self.image_handler = ImageLoader()
        self.image_handler.load_images(program_state=program_state)
        self.sprite_handler = SpriteLoader(self.image_handler)
        self.button_handler = ButtonHandler()
        self.gameplay_handler = GamePlayHandler()
        self.notification_handler = NotificationHandler()

    def handle_setup(self, program_state: ProgramState, asset_information: AssetInformation) -> None:
        if program_state.game_state == GameState.MENU:
            if self.button_handler.menu_state == 'main':
                self.gameplay_handler.game_board = None
            self.button_handler.menu_setup(program_state, asset_information, self.sprite_handler)

        elif program_state.game_state == GameState.GAMEPLAY:
            self.gameplay_handler.gameplay_setup(asset_information, self.sprite_handler)

        elif program_state.game_state == GameState.INFO_DISPLAY:
            self.notification_handler.notification_setup(program_state, asset_information, self.sprite_handler)

        program_state.dirty = True
        program_state.setup_needed = False

    def handle_frame(self, program_state: ProgramState, asset_information: AssetInformation,
                     mouse_event: namedtuple) -> None:
        if program_state.game_state == GameState.MENU:
            self.button_handler.button_frame(program_state, asset_information, mouse_event)

        elif program_state.game_state == GameState.GAMEPLAY:
            self.button_handler.button_frame(program_state, asset_information, mouse_event)
            self.gameplay_handler.gameplay_frame(program_state, mouse_event)

        elif program_state.game_state == GameState.INFO_DISPLAY:
            self.notification_handler.notification_frame(program_state, asset_information, mouse_event.clicked)


# Helper Functions for helping 'program_loop'

def handle_user_input(program_state: ProgramState, current_screen_size: Tuple[int, int]) -> namedtuple:
    MouseEvent = namedtuple('MouseEvent', ['pos', 'clicked'])
    report = None

    try:
        mouse_pos = pygame.mouse.get_pos()
        virtual_mouse_pos = (mouse_pos[0] * 960 // current_screen_size[0],
                             mouse_pos[1] * 640 // current_screen_size[1])
        try:
            player_clicked = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    program_state.running = False
                    break
                else:
                    if event.type == pygame.MOUSEBUTTONUP:
                        player_clicked = True

            report = MouseEvent(pos=virtual_mouse_pos, clicked=player_clicked)

        except pygame.error as e:
            program_state.handle_error("Error getting events", e)

    except pygame.error as e:
        program_state.handle_error("Error getting mouse position", e)

    return report


def update_display(program_state: ProgramState, asset_information: AssetInformation, virtual_screen: pygame.Surface,
                   screen: pygame.Surface) -> None:
    asset_information.active_sprites.clear(virtual_screen, asset_information.background_image)
    asset_information.active_sprites.draw(virtual_screen)
    try:
        current_screen_size = screen.get_size()
        scaled_screen = pygame.transform.scale(virtual_screen, current_screen_size)
        screen.blit(scaled_screen, (0, 0))
    except pygame.error as e:
        print(f"Error scaling surface: {e}")
        program_state.handle_error("Error scaling surface", e)
    try:
        pygame.display.update()
    except pygame.error as e:
        program_state.handle_error("Error updating display", e)


# Primary Game Loop

def program_loop(clock: pygame.time.Clock, screen: pygame.Surface) -> None:
    active_screen_size = screen.get_size()
    SCREEN_SIZE_DICT = {0: [720, 480], 1: [864, 576], 2: [960, 640], 3: [1080, 720], 4: [1296, 864]}

    VIRTUAL_SCREEN_SIZE = [960, 640]
    virtual_screen = pygame.Surface(VIRTUAL_SCREEN_SIZE)

    program_state = ProgramState()
    asset_information = AssetInformation()
    primary_manager = HandlerManager(program_state)

    while program_state.running:
        mouse_event = handle_user_input(program_state, active_screen_size)

        if program_state.setup_needed:
            if program_state.setting_changed_flags[1]:
                active_screen_size = SCREEN_SIZE_DICT[settings.screen_size]
                try:
                    screen = pygame.display.set_mode(active_screen_size)
                except pygame.error as e:
                    program_state.handle_error("Error setting display mode", e)
            primary_manager.handle_setup(program_state, asset_information)

        primary_manager.handle_frame(program_state, asset_information, mouse_event)

        if program_state.dirty:
            update_display(program_state, asset_information, virtual_screen, screen)
            program_state.dirty = False

        clock.tick(60)

    pygame.quit()
    sys.exit(program_state.program_return_value)


# Main Function

def main() -> None:
    try:
        INITIAL_SCREEN_SIZE = [960, 640]
        pygame.init()
        pygame.display.set_caption("Tower of Hanoi")
        Clock = pygame.time.Clock()
        Screen = pygame.display.set_mode(INITIAL_SCREEN_SIZE)
        program_loop(Clock, Screen)
    except pygame.error as e:
        print("Error: Failed to initialize Pygame or set display mode:", e)
        pygame.quit()
        sys.exit(1)


if __name__ == '__main__':
    main()

