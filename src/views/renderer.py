import pygame
from typing import Union
from src.constants import MenuState, GameNotification
from src.models.button_entity import ButtonEntity
from src.models.menu_model import MenuModel
from src.models.game_model import GameModel
from src.views.assets import AssetsContainer


class GameRenderer:
    """
    Renders both menu system and game board to the screen.

    This class handles all visual presentation, drawing backgrounds, buttons,
    discs, indicators, and notifications based on the current state of whichever
    model is active.

    Attributes:
        assets: AssetsContainer with all visual resources.
        TOWER_CENTERS: X-coordinates of the three tower centers.
        BASE_DISC_WIDTH: Half-width of the smallest disc.
        DISC_WIDTH_INCREMENT: Width increase for each larger disc size.
        DISC_HEIGHT: Height of each disc.
        BASE_Y: Y-coordinate of the top of the lowest disc.
        SETTING_INDICATOR_POSITIONS: Positions for option menu indicators.
        NOTIFICATION_POSITIONS: Positions for game notification messages.
    """
    # Class constants for positioning and dimensions
    TOWER_CENTERS = [192, 480, 768]  # X-coordinates of tower centers
    BASE_DISC_WIDTH = 43  # Half-width of the smallest disc
    DISC_WIDTH_INCREMENT = 21  # How much wider each size gets
    DISC_HEIGHT = 69  # Height of each disc
    BASE_Y = 516  # Y-coordinate of the top of the lowest disc

    SETTING_INDICATOR_POSITIONS = {
        "difficulty": (550, 160),
        "resolution": (550, 300),
        "theme": (550, 420)
    }

    NOTIFICATION_POSITIONS = {
        GameNotification.ILLEGAL_MOVE: 20,  # Top Y position for illegal move
        GameNotification.VICTORY: 160  # Top Y position for victory
    }

    def __init__(self, asset_container: AssetsContainer):
        """
        Initialize a new GameRenderer with the provided assets.

        Args:
            asset_container: An AssetsContainer with all visual resources.
        """
        self.assets = asset_container

    def update_assets(self, asset_container: AssetsContainer):
        """
        Update the renderer to use a new set of assets.

        Called when the user changes the visual theme.

        Args:
            asset_container: The new AssetsContainer to use.
        """
        self.assets = asset_container

    def _draw_button(self, model: Union[MenuModel, GameModel], button: ButtonEntity, screen: pygame.Surface) -> None:
        """
        Draw a button on the screen with appropriate highlighting.

        Args:
            model: The current model containing button highlight information.
            button: The ButtonEntity to draw.
            screen: The Pygame surface to draw on.
        """
        button_highlighted = False
        if model.highlighted_button:
            if model.highlighted_button.flag == button.flag:
                button_highlighted = True

        if button_highlighted:
            button_image = self.assets.buttons.highlighted[button.flag]
        else:
            button_image = self.assets.buttons.standard[button.flag]
        button_pos = button.rect.topleft
        screen.blit(button_image, button_pos)

    def _draw_menu_background(self, model: MenuModel, screen: pygame.Surface) -> None:
        """
        Draw the appropriate background based on the current menu state.

        Args:
            model: The MenuModel containing the current menu state.
            screen: The Pygame surface to draw on.
        """
        if model.current_menu == MenuState.MAIN:
            background_image = self.assets.backgrounds.main_menu
        elif model.current_menu == MenuState.OPTIONS:
            background_image = self.assets.backgrounds.options_menu
        elif model.current_menu == MenuState.CREDITS:
            background_image = self.assets.backgrounds.credits
        else:
            background_image = pygame.Surface((0, 0))
        screen.blit(background_image, [0, 0])

    def _draw_settings_indicators(self, model: MenuModel, screen: pygame.Surface) -> None:
        """
        Draw the current settings indicators in the options menu.

        Visualizes the current theme, resolution, and difficulty settings.

        Args:
            model: The MenuModel containing the settings information.
            screen: The Pygame surface to draw on.
        """
        theme_indicator = self.assets.setting_indicators.theme[model.settings_select_display[0]]
        resolution_indicator = self.assets.setting_indicators.resolution[model.settings_select_display[1]]
        difficulty_indicator = self.assets.setting_indicators.difficulty[model.settings_select_display[2]]

        screen.blit(difficulty_indicator, self.SETTING_INDICATOR_POSITIONS["difficulty"])
        screen.blit(resolution_indicator, self.SETTING_INDICATOR_POSITIONS["resolution"])
        screen.blit(theme_indicator, self.SETTING_INDICATOR_POSITIONS["theme"])

    def _draw_tutorial(self, model: MenuModel, screen: pygame.Surface) -> None:
        """
        Draw the current tutorial slide.

        Args:
            model: The MenuModel containing the current tutorial slide index.
            screen: The Pygame surface to draw on.
        """
        slide_image = self.assets.tutorial_images.slides[model.tutorial_slide]
        screen.blit(slide_image, [0, 0])

    def render_menu(self, model: MenuModel, screen: pygame.Surface) -> None:
        """
        Render the complete menu screen based on the current menu state.

        Draws the appropriate background, buttons, and any additional elements
        specific to the current menu state (settings indicators, tutorial slides).

        Args:
            model: The MenuModel to render.
            screen: The Pygame surface to draw on.
        """
        self._draw_menu_background(model, screen)
        for button in model.active_buttons:
            self._draw_button(model, button, screen)
        if model.current_menu == MenuState.OPTIONS:
            self._draw_settings_indicators(model, screen)
        if model.current_menu == MenuState.TUTORIAL:
            self._draw_tutorial(model, screen)

    def _draw_single_disc(self, tower: int, disc_size: int, height: int, highlight: bool,
                          screen: pygame.Surface) -> None:
        """
        Draw a single disc on a tower.

        Args:
            tower: The tower index (0, 1, or 2) to draw the disc on.
            disc_size: The size of the disc (0-4, with 4 being the largest).
            height: The vertical position of the disc in the stack.
            highlight: Whether to draw the disc highlighted.
            screen: The Pygame surface to draw on.
        """
        disc_image = self.assets.discs.highlighted[disc_size] if highlight else self.assets.discs.standard[disc_size]

        # Calculate positions
        x_position = self.TOWER_CENTERS[tower] - self.BASE_DISC_WIDTH - (self.DISC_WIDTH_INCREMENT * disc_size)
        y_position = self.BASE_Y - (self.DISC_HEIGHT * height)

        # Draw the disc
        screen.blit(disc_image, [x_position, y_position])

    def _draw_game_discs(self, model: GameModel, screen: pygame.Surface) -> None:
        """
        Draw all discs on their respective towers.

        Highlights the top disc of the selected tower if one is selected.

        Args:
            model: The GameModel containing the tower and disc data.
            screen: The Pygame surface to draw on.
        """
        for tower_indx in range(3):
            active_tower = model.towers[tower_indx]
            for disc_indx in range(len(active_tower)):
                if model.selected_tower == tower_indx and active_tower[disc_indx] == active_tower[-1]:
                    highlight = True
                else:
                    highlight = False
                self._draw_single_disc(tower_indx, active_tower[disc_indx], disc_indx, highlight, screen)

    def _draw_game_notification(self, model: GameModel, screen: pygame.Surface) -> None:
        """
        Draw the current game notification message.

        Displays notifications for illegal moves or victory.

        Args:
            model: The GameModel containing the notification type.
            screen: The Pygame surface to draw on.
        """
        notification_image = {
            GameNotification.ILLEGAL_MOVE: self.assets.game_notifications.illegal_move,
            GameNotification.VICTORY: self.assets.game_notifications.victory
        }[model.notification]

        notification_top = self.NOTIFICATION_POSITIONS[model.notification]
        image_size = notification_image.get_size()
        notification_location = [480 - (image_size[0] // 2), notification_top]
        screen.blit(notification_image, notification_location)

    def render_game(self, model: GameModel, screen: pygame.Surface) -> None:
        """
        Render the complete game screen.

        Draws the game board background, all discs on their towers, game interface
        buttons, and any active notification messages.

        Args:
            model: The GameModel to render.
            screen: The Pygame surface to draw on.
        """
        background_image = self.assets.backgrounds.game_board
        screen.blit(background_image, [0, 0])
        self._draw_game_discs(model, screen)
        for button in model.active_buttons:
            self._draw_button(model, button, screen)
        if model.notification is not None:
            self._draw_game_notification(model, screen)
