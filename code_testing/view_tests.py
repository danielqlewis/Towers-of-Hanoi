import unittest
from unittest.mock import Mock, patch, MagicMock
import pygame
from src.constants import MenuState, ButtonFlag, GameNotification, MenuTheme
from src.models.button_entity import ButtonEntity
from src.models.menu_model import MenuModel
from src.models.game_model import GameModel
from src.views.renderer import GameRenderer
from src.views.assets import (
    AssetsContainer, BackgroundContainer, ButtonContainer,
    DiscContainer, SettingIndicatorContainer, GameNotificationContainer, TutorialSlidesContainer,
    get_theme_specific_assets, get_common_assets, build_asset_container
)


class TestAssetsContainer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialize pygame for all tests."""
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        """Quit pygame after all tests."""
        pygame.quit()

    def setUp(self):
        """Set up test fixtures before each test."""
        # Create mock surfaces to use throughout tests
        self.mock_surface = MagicMock(spec=pygame.Surface)

        # Mock the load_image functions to avoid actual file loading
        self.patcher1 = patch('src.views.assets.load_image')
        self.mock_load_image = self.patcher1.start()
        self.mock_load_image.return_value = self.mock_surface

        self.patcher2 = patch('src.views.assets.load_image_with_alpha')
        self.mock_load_image_with_alpha = self.patcher2.start()
        self.mock_load_image_with_alpha.return_value = self.mock_surface

    def tearDown(self):
        """Clean up after each test."""
        self.patcher1.stop()
        self.patcher2.stop()

    def test_background_container(self):
        """Test the BackgroundContainer dataclass."""
        bg = BackgroundContainer(
            main_menu=self.mock_surface,
            options_menu=self.mock_surface,
            game_board=self.mock_surface,
            credits=self.mock_surface
        )

        # Verify properties
        self.assertEqual(bg.main_menu, self.mock_surface)
        self.assertEqual(bg.options_menu, self.mock_surface)
        self.assertEqual(bg.game_board, self.mock_surface)
        self.assertEqual(bg.credits, self.mock_surface)

        # Verify immutability
        with self.assertRaises(Exception):  # dataclass is frozen, so this should fail
            bg.main_menu = MagicMock(spec=pygame.Surface)

    def test_button_container(self):
        """Test the ButtonContainer dataclass for assets."""
        button_dict = {
            ButtonFlag.PLAY: self.mock_surface,
            ButtonFlag.OPTIONS: self.mock_surface,
            ButtonFlag.RESET_BOARD: self.mock_surface
        }
        bc = ButtonContainer(standard=button_dict, highlighted=button_dict)

        # Verify properties
        self.assertEqual(bc.standard, button_dict)
        self.assertEqual(bc.highlighted, button_dict)

        # Test with various ButtonFlags
        for flag in [ButtonFlag.PLAY, ButtonFlag.OPTIONS, ButtonFlag.RESET_BOARD]:
            self.assertIn(flag, bc.standard)
            self.assertIn(flag, bc.highlighted)

        # Verify immutability
        with self.assertRaises(Exception):
            bc.standard = {}

    def test_disc_container(self):
        """Test the DiscContainer dataclass."""
        disc_dict = {0: self.mock_surface, 1: self.mock_surface}
        dc = DiscContainer(standard=disc_dict, highlighted=disc_dict)

        # Verify properties
        self.assertEqual(dc.standard, disc_dict)
        self.assertEqual(dc.highlighted, disc_dict)

        # Verify immutability
        with self.assertRaises(Exception):
            dc.standard = {}

    def test_setting_indicator_container(self):
        """Test the SettingIndicatorContainer dataclass."""
        difficulty_dict = {3: self.mock_surface}
        resolution_dict = {(960, 640): self.mock_surface}
        theme_dict = {MenuTheme.STANDARD: self.mock_surface}

        sic = SettingIndicatorContainer(
            difficulty=difficulty_dict,
            resolution=resolution_dict,
            theme=theme_dict
        )

        # Verify properties
        self.assertEqual(sic.difficulty, difficulty_dict)
        self.assertEqual(sic.resolution, resolution_dict)
        self.assertEqual(sic.theme, theme_dict)

        # Verify immutability
        with self.assertRaises(Exception):
            sic.difficulty = {}

    def test_game_notification_container(self):
        """Test the GameNotificationContainer dataclass."""
        gnc = GameNotificationContainer(
            illegal_move=self.mock_surface,
            victory=self.mock_surface
        )

        # Verify properties
        self.assertEqual(gnc.illegal_move, self.mock_surface)
        self.assertEqual(gnc.victory, self.mock_surface)

        # Verify immutability
        with self.assertRaises(Exception):
            gnc.illegal_move = MagicMock(spec=pygame.Surface)

    def test_tutorial_slides_container(self):
        """Test the TutorialSlidesContainer dataclass."""
        slides_dict = {0: self.mock_surface, 1: self.mock_surface}
        tsc = TutorialSlidesContainer(slides=slides_dict)

        # Verify properties
        self.assertEqual(tsc.slides, slides_dict)

        # Verify immutability
        with self.assertRaises(Exception):
            tsc.slides = {}

    def test_assets_container(self):
        """Test the main AssetsContainer dataclass."""
        # Create mock containers
        bg = BackgroundContainer(
            main_menu=self.mock_surface,
            options_menu=self.mock_surface,
            game_board=self.mock_surface,
            credits=self.mock_surface
        )

        buttons = ButtonContainer(
            standard={ButtonFlag.PLAY: self.mock_surface},
            highlighted={ButtonFlag.PLAY: self.mock_surface}
        )

        discs = DiscContainer(
            standard={0: self.mock_surface},
            highlighted={0: self.mock_surface}
        )

        settings = SettingIndicatorContainer(
            difficulty={3: self.mock_surface},
            resolution={(960, 640): self.mock_surface},
            theme={MenuTheme.STANDARD: self.mock_surface}
        )

        notifications = GameNotificationContainer(
            illegal_move=self.mock_surface,
            victory=self.mock_surface
        )

        tutorials = TutorialSlidesContainer(
            slides={0: self.mock_surface}
        )

        # Create AssetsContainer
        ac = AssetsContainer(
            backgrounds=bg,
            buttons=buttons,
            discs=discs,
            setting_indicators=settings,
            game_notifications=notifications,
            tutorial_images=tutorials
        )

        # Verify properties
        self.assertEqual(ac.backgrounds, bg)
        self.assertEqual(ac.buttons, buttons)
        self.assertEqual(ac.discs, discs)
        self.assertEqual(ac.setting_indicators, settings)
        self.assertEqual(ac.game_notifications, notifications)
        self.assertEqual(ac.tutorial_images, tutorials)

        # Verify immutability
        with self.assertRaises(Exception):
            ac.backgrounds = MagicMock(spec=BackgroundContainer)

    def test_get_theme_specific_assets(self):
        """Test get_theme_specific_assets function for different themes."""
        # Test STANDARD theme
        main_menu, options_menu, game_board = get_theme_specific_assets(MenuTheme.STANDARD)

        # Verify the correct paths were used for loading
        self.mock_load_image.assert_any_call("default/Menu_BG.png")
        self.mock_load_image.assert_any_call("default/Options_BG.png")
        self.mock_load_image.assert_any_call("default/Game_BG.png")

        # Reset mock to test RED theme
        self.mock_load_image.reset_mock()

        # Test RED theme
        main_menu, options_menu, game_board = get_theme_specific_assets(MenuTheme.RED)

        # Verify the correct paths were used for loading
        self.mock_load_image.assert_any_call("red/Menu_BG.png")
        self.mock_load_image.assert_any_call("red/Options_BG.png")
        self.mock_load_image.assert_any_call("red/Game_BG.png")

        # Reset mock to test BLUE theme
        self.mock_load_image.reset_mock()

        # Test BLUE theme
        main_menu, options_menu, game_board = get_theme_specific_assets(MenuTheme.BLUE)

        # Verify the correct paths were used for loading
        self.mock_load_image.assert_any_call("blue/Menu_BG.png")
        self.mock_load_image.assert_any_call("blue/Options_BG.png")
        self.mock_load_image.assert_any_call("blue/Game_BG.png")

    def test_get_common_assets(self):
        """Test get_common_assets function."""
        common_assets = get_common_assets()

        # Verify all required assets are present
        self.assertIn("credits", common_assets)
        self.assertIn("button_assets", common_assets)
        self.assertIn("disc_assets", common_assets)
        self.assertIn("setting_indicator_assets", common_assets)
        self.assertIn("notification_assets", common_assets)
        self.assertIn("tutorial_assets", common_assets)

        # Verify structures of the assets
        self.assertIsInstance(common_assets["button_assets"], ButtonContainer)
        self.assertIsInstance(common_assets["disc_assets"], DiscContainer)
        self.assertIsInstance(common_assets["setting_indicator_assets"], SettingIndicatorContainer)
        self.assertIsInstance(common_assets["notification_assets"], GameNotificationContainer)
        self.assertIsInstance(common_assets["tutorial_assets"], TutorialSlidesContainer)

        # Verify button assets contain expected buttons
        button_assets = common_assets["button_assets"]
        expected_buttons = [
            ButtonFlag.PLAY, ButtonFlag.OPTIONS, ButtonFlag.EXIT,
            ButtonFlag.TUTORIAL, ButtonFlag.CREDITS, ButtonFlag.DIFFICULTY_TOGGLE,
            ButtonFlag.RESOLUTION_TOGGLE, ButtonFlag.THEME_TOGGLE,
            ButtonFlag.BACK_TO_MAIN, ButtonFlag.ACCEPT_SETTINGS, ButtonFlag.RESET_BOARD
        ]

        for button in expected_buttons:
            self.assertIn(button, button_assets.standard)
            self.assertIn(button, button_assets.highlighted)

        # Verify disc loading
        self.assertEqual(len(common_assets["disc_assets"].standard), 5)  # 5 discs (0-4)
        self.assertEqual(len(common_assets["disc_assets"].highlighted), 5)

        # Verify setting indicators
        self.assertEqual(len(common_assets["setting_indicator_assets"].difficulty), 3)  # 3 difficulty levels
        self.assertEqual(len(common_assets["setting_indicator_assets"].resolution), 5)  # 5 resolutions
        self.assertEqual(len(common_assets["setting_indicator_assets"].theme), 3)  # 3 themes

        # Verify tutorial slides
        self.assertEqual(len(common_assets["tutorial_assets"].slides), 8)  # 8 tutorial slides

    @patch('src.views.assets.logger')
    def test_build_asset_container_success(self, mock_logger):
        """Test successful asset container building."""
        # Set up mocks for theme-specific and common assets
        asset_container = build_asset_container(MenuTheme.STANDARD)

        # Verify the returned container
        self.assertIsNotNone(asset_container)
        self.assertIsInstance(asset_container, AssetsContainer)
        self.assertIsInstance(asset_container.backgrounds, BackgroundContainer)
        self.assertIsInstance(asset_container.buttons, ButtonContainer)
        self.assertIsInstance(asset_container.discs, DiscContainer)
        self.assertIsInstance(asset_container.setting_indicators, SettingIndicatorContainer)
        self.assertIsInstance(asset_container.game_notifications, GameNotificationContainer)
        self.assertIsInstance(asset_container.tutorial_images, TutorialSlidesContainer)

        # Verify logger wasn't called with error
        mock_logger.error.assert_not_called()

    @patch('src.views.assets.get_theme_specific_assets')
    @patch('src.views.assets.logger')
    def test_build_asset_container_theme_failure(self, mock_logger, mock_get_theme):
        """Test asset container building with theme asset failure."""
        # Make theme-specific assets fail
        mock_get_theme.side_effect = pygame.error("Test error")

        # Try to build container
        asset_container = build_asset_container(MenuTheme.STANDARD)

        # Verify error handling
        self.assertIsNone(asset_container)
        mock_logger.error.assert_called_once()
        self.assertIn("Failed to load theme asset", mock_logger.error.call_args[0][0])

    @patch('src.views.assets.get_common_assets')
    @patch('src.views.assets.logger')
    def test_build_asset_container_common_failure(self, mock_logger, mock_get_common):
        """Test asset container building with common asset failure."""
        # Make common assets fail
        mock_get_common.side_effect = FileNotFoundError("Test error")

        # Try to build container
        asset_container = build_asset_container(MenuTheme.STANDARD)

        # Verify error handling
        self.assertIsNone(asset_container)
        mock_logger.error.assert_called_once()
        self.assertIn("Failed to load common asset", mock_logger.error.call_args[0][0])


class TestGameRenderer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialize pygame for all tests."""
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        """Quit pygame after all tests."""
        pygame.quit()

    def setUp(self):
        """Set up test fixtures before each test."""
        # Create mock surfaces for testing
        self.mock_surface = MagicMock(spec=pygame.Surface)
        self.mock_surface.get_size.return_value = (100, 100)

        # Create mock screen
        self.mock_screen = MagicMock(spec=pygame.Surface)

        # Create mock assets container with all required assets
        self.mock_assets = self._create_mock_assets()

        # Create the renderer
        self.renderer = GameRenderer(self.mock_assets)

        # Create mock models
        self.menu_model = self._create_mock_menu_model()
        self.game_model = self._create_mock_game_model()

    def _create_mock_assets(self):
        """Helper to create a complete mock assets container."""
        # Create background container
        bg = Mock(spec=BackgroundContainer)
        bg.main_menu = self.mock_surface
        bg.options_menu = self.mock_surface
        bg.game_board = self.mock_surface
        bg.credits = self.mock_surface

        # Create button container - note this is the assets.ButtonContainer
        button_std = {flag: self.mock_surface for flag in ButtonFlag}
        button_high = {flag: self.mock_surface for flag in ButtonFlag}
        buttons = Mock(spec=ButtonContainer)
        buttons.standard = button_std
        buttons.highlighted = button_high

        # Create disc container
        disc_std = {i: self.mock_surface for i in range(5)}
        disc_high = {i: self.mock_surface for i in range(5)}
        discs = Mock(spec=DiscContainer)
        discs.standard = disc_std
        discs.highlighted = disc_high

        # Create setting indicators
        difficulty_indicators = {i: self.mock_surface for i in range(3, 6)}
        resolution_indicators = {
            (720, 480): self.mock_surface,
            (864, 576): self.mock_surface,
            (960, 640): self.mock_surface,
            (1080, 720): self.mock_surface,
            (1296, 864): self.mock_surface
        }
        theme_indicators = {theme: self.mock_surface for theme in MenuTheme}
        settings = Mock(spec=SettingIndicatorContainer)
        settings.difficulty = difficulty_indicators
        settings.resolution = resolution_indicators
        settings.theme = theme_indicators

        # Create notification container
        notifications = Mock(spec=GameNotificationContainer)
        notifications.illegal_move = self.mock_surface
        notifications.victory = self.mock_surface

        # Create tutorial container
        tutorials = Mock(spec=TutorialSlidesContainer)
        tutorials.slides = {i: self.mock_surface for i in range(8)}

        # Create assets container
        assets = Mock(spec=AssetsContainer)
        assets.backgrounds = bg
        assets.buttons = buttons
        assets.discs = discs
        assets.setting_indicators = settings
        assets.game_notifications = notifications
        assets.tutorial_images = tutorials

        return assets

    def _create_mock_menu_model(self):
        """Helper to create a mock menu model."""
        model = Mock(spec=MenuModel)
        model.current_menu = MenuState.MAIN
        model.highlighted_button = None

        # Create buttons using the actual ButtonEntity class
        button1 = ButtonEntity(ButtonFlag.PLAY)
        button2 = ButtonEntity(ButtonFlag.OPTIONS)

        model.active_buttons = [button1, button2]

        # Settings display
        model.settings_select_display = [MenuTheme.STANDARD, (960, 640), 3]

        # Tutorial
        model.tutorial_slide = 0

        return model

    def _create_mock_game_model(self):
        """Helper to create a mock game model."""
        model = Mock(spec=GameModel)
        model.highlighted_button = None
        model.selected_tower = None
        model.notification = None

        # Tower configuration: ([2, 1, 0], [], [])
        model.towers = ([2, 1, 0], [], [])

        # Create buttons using the actual ButtonEntity class
        button = ButtonEntity(ButtonFlag.RESET_BOARD)
        button_back = ButtonEntity(ButtonFlag.BACK_TO_MAIN)

        model.active_buttons = [button, button_back]

        return model

    def test_draw_button_standard(self):
        """Test drawing a standard (non-highlighted) button."""
        # Use a button from the mock model (this is models.ButtonEntity)
        button = self.menu_model.active_buttons[0]

        # Ensure model has no highlighted button
        self.menu_model.highlighted_button = None

        # Call the draw button method
        self.renderer._draw_button(self.menu_model, button, self.mock_screen)

        # Verify the standard button image was used from assets
        self.mock_screen.blit.assert_called_once_with(
            self.mock_assets.buttons.standard[button.flag],
            button.rect.topleft
        )

    def test_draw_button_highlighted(self):
        """Test drawing a highlighted button."""
        # Use a button from the mock model (this is models.ButtonEntity)
        button = self.menu_model.active_buttons[0]

        # Create highlighted button
        highlight = ButtonEntity(button.flag)
        self.menu_model.highlighted_button = highlight

        # Call the draw button method
        self.renderer._draw_button(self.menu_model, button, self.mock_screen)

        # Verify the highlighted button image was used from assets
        self.mock_screen.blit.assert_called_once_with(
            self.mock_assets.buttons.highlighted[button.flag],
            button.rect.topleft
        )

    def test_draw_menu_background_main(self):
        """Test drawing the main menu background."""
        self.menu_model.current_menu = MenuState.MAIN

        self.renderer._draw_menu_background(self.menu_model, self.mock_screen)

        self.mock_screen.blit.assert_called_once_with(self.mock_assets.backgrounds.main_menu, [0, 0])

    def test_draw_menu_background_options(self):
        """Test drawing the options menu background."""
        self.menu_model.current_menu = MenuState.OPTIONS

        self.renderer._draw_menu_background(self.menu_model, self.mock_screen)

        self.mock_screen.blit.assert_called_once_with(self.mock_assets.backgrounds.options_menu, [0, 0])

    def test_draw_menu_background_credits(self):
        """Test drawing the credits background."""
        self.menu_model.current_menu = MenuState.CREDITS

        self.renderer._draw_menu_background(self.menu_model, self.mock_screen)

        self.mock_screen.blit.assert_called_once_with(self.mock_assets.backgrounds.credits, [0, 0])

    def test_draw_settings_indicators(self):
        """Test drawing the settings indicators."""
        self.renderer._draw_settings_indicators(self.menu_model, self.mock_screen)

        # Verify all three indicators were drawn
        self.assertEqual(self.mock_screen.blit.call_count, 3)

        # Get all call arguments
        calls = self.mock_screen.blit.call_args_list

        # Verify each indicator was drawn in the correct position
        expected_positions = [
            self.renderer.SETTING_INDICATOR_POSITIONS["difficulty"],
            self.renderer.SETTING_INDICATOR_POSITIONS["resolution"],
            self.renderer.SETTING_INDICATOR_POSITIONS["theme"]
        ]

        for i, pos in enumerate(expected_positions):
            self.assertEqual(calls[i][0][1], pos)

    def test_draw_tutorial(self):
        """Test drawing a tutorial slide."""
        self.menu_model.tutorial_slide = 3

        self.renderer._draw_tutorial(self.menu_model, self.mock_screen)

        self.mock_screen.blit.assert_called_once_with(
            self.mock_assets.tutorial_images.slides[3],
            [0, 0]
        )

    def test_render_menu_main(self):
        """Test rendering the main menu."""
        self.menu_model.current_menu = MenuState.MAIN

        with patch.object(self.renderer, '_draw_menu_background') as mock_bg, \
                patch.object(self.renderer, '_draw_button') as mock_btn, \
                patch.object(self.renderer, '_draw_settings_indicators') as mock_settings, \
                patch.object(self.renderer, '_draw_tutorial') as mock_tutorial:
            self.renderer.render_menu(self.menu_model, self.mock_screen)

            # Check background was drawn
            mock_bg.assert_called_once_with(self.menu_model, self.mock_screen)

            # Check buttons were drawn (2 buttons in our mock)
            self.assertEqual(mock_btn.call_count, 2)
            # Verify specific buttons were drawn
            mock_btn.assert_any_call(self.menu_model, self.menu_model.active_buttons[0], self.mock_screen)
            mock_btn.assert_any_call(self.menu_model, self.menu_model.active_buttons[1], self.mock_screen)

            # Check settings were not drawn (only for options menu)
            mock_settings.assert_not_called()

            # Check tutorial was not drawn (only for tutorial state)
            mock_tutorial.assert_not_called()

    def test_render_menu_options(self):
        """Test rendering the options menu."""
        self.menu_model.current_menu = MenuState.OPTIONS

        # Update the model's active buttons to be options buttons
        options_buttons = [
            ButtonEntity(ButtonFlag.DIFFICULTY_TOGGLE),
            ButtonEntity(ButtonFlag.RESOLUTION_TOGGLE)
        ]
        self.menu_model.active_buttons = options_buttons

        with patch.object(self.renderer, '_draw_menu_background') as mock_bg, \
                patch.object(self.renderer, '_draw_button') as mock_btn, \
                patch.object(self.renderer, '_draw_settings_indicators') as mock_settings, \
                patch.object(self.renderer, '_draw_tutorial') as mock_tutorial:
            self.renderer.render_menu(self.menu_model, self.mock_screen)

            # Check all appropriate methods were called
            mock_bg.assert_called_once()
            self.assertEqual(mock_btn.call_count, 2)  # 2 buttons in our mock

            # Verify specific buttons were drawn
            mock_btn.assert_any_call(self.menu_model, options_buttons[0], self.mock_screen)
            mock_btn.assert_any_call(self.menu_model, options_buttons[1], self.mock_screen)

            mock_settings.assert_called_once()
            mock_tutorial.assert_not_called()

    def test_render_menu_tutorial(self):
        """Test rendering the tutorial menu."""
        self.menu_model.current_menu = MenuState.TUTORIAL

        with patch.object(self.renderer, '_draw_menu_background') as mock_bg, \
                patch.object(self.renderer, '_draw_button') as mock_btn, \
                patch.object(self.renderer, '_draw_settings_indicators') as mock_settings, \
                patch.object(self.renderer, '_draw_tutorial') as mock_tutorial:
            self.renderer.render_menu(self.menu_model, self.mock_screen)

            # Check all appropriate methods were called
            mock_bg.assert_called_once()
            self.assertEqual(mock_btn.call_count, 2)  # 2 buttons in our mock
            mock_settings.assert_not_called()
            mock_tutorial.assert_called_once()

    def test_draw_single_disc(self):
        """Test drawing a single disc."""
        # Test drawing a non-highlighted disc
        self.renderer._draw_single_disc(0, 2, 1, False, self.mock_screen)

        # Calculate expected position
        tower_center = self.renderer.TOWER_CENTERS[0]
        base_width = self.renderer.BASE_DISC_WIDTH
        width_increment = self.renderer.DISC_WIDTH_INCREMENT
        disc_height = self.renderer.DISC_HEIGHT
        base_y = self.renderer.BASE_Y

        expected_x = tower_center - base_width - (width_increment * 2)
        expected_y = base_y - (disc_height * 1)

        # Verify the standard disc was used at correct position
        self.mock_screen.blit.assert_called_once_with(
            self.mock_assets.discs.standard[2],
            [expected_x, expected_y]
        )

        # Reset and test highlighted disc
        self.mock_screen.blit.reset_mock()
        self.renderer._draw_single_disc(1, 0, 2, True, self.mock_screen)

        # Calculate new expected position
        tower_center = self.renderer.TOWER_CENTERS[1]
        expected_x = tower_center - base_width - (width_increment * 0)
        expected_y = base_y - (disc_height * 2)

        # Verify the highlighted disc was used at correct position
        self.mock_screen.blit.assert_called_once_with(
            self.mock_assets.discs.highlighted[0],
            [expected_x, expected_y]
        )

    def test_draw_game_discs(self):
        """Test drawing all discs for the game."""
        with patch.object(self.renderer, '_draw_single_disc') as mock_draw:
            # Initial tower configuration from mock: ([2, 1, 0], [], [])
            self.game_model.selected_tower = None

            self.renderer._draw_game_discs(self.game_model, self.mock_screen)

            # Verify three discs were drawn (one for each in first tower)
            self.assertEqual(mock_draw.call_count, 3)

            # Check the calls match expected disc positions and highlighting
            mock_draw.assert_any_call(0, 2, 0, False, self.mock_screen)  # Bottom disc
            mock_draw.assert_any_call(0, 1, 1, False, self.mock_screen)  # Middle disc
            mock_draw.assert_any_call(0, 0, 2, False, self.mock_screen)  # Top disc

            # Test with selected tower
            mock_draw.reset_mock()
            self.game_model.selected_tower = 0

            self.renderer._draw_game_discs(self.game_model, self.mock_screen)

            # Verify three discs were drawn with top one highlighted
            self.assertEqual(mock_draw.call_count, 3)
            mock_draw.assert_any_call(0, 2, 0, False, self.mock_screen)  # Bottom disc
            mock_draw.assert_any_call(0, 1, 1, False, self.mock_screen)  # Middle disc
            mock_draw.assert_any_call(0, 0, 2, True, self.mock_screen)  # Top disc (highlighted)

    def test_draw_game_notification_illegal_move(self):
        """Test drawing an illegal move notification."""
        self.game_model.notification = GameNotification.ILLEGAL_MOVE

        self.renderer._draw_game_notification(self.game_model, self.mock_screen)

        # Calculate expected position
        notification_top = self.renderer.NOTIFICATION_POSITIONS[GameNotification.ILLEGAL_MOVE]
        expected_pos = [480 - 50, notification_top]  # 50 is half the width (100/2) from mock surface

        self.mock_screen.blit.assert_called_once_with(
            self.mock_assets.game_notifications.illegal_move,
            expected_pos
        )

    def test_draw_game_notification_victory(self):
        """Test drawing a victory notification."""
        self.game_model.notification = GameNotification.VICTORY

        self.renderer._draw_game_notification(self.game_model, self.mock_screen)

        # Calculate expected position
        notification_top = self.renderer.NOTIFICATION_POSITIONS[GameNotification.VICTORY]
        expected_pos = [480 - 50, notification_top]  # 50 is half the width (100/2) from mock surface

        self.mock_screen.blit.assert_called_once_with(
            self.mock_assets.game_notifications.victory,
            expected_pos
        )

    def test_render_game(self):
        """Test rendering the full game."""
        with patch.object(self.renderer, '_draw_game_discs') as mock_discs, \
                patch.object(self.renderer, '_draw_button') as mock_btn, \
                patch.object(self.renderer, '_draw_game_notification') as mock_notif:
            # Without notification
            self.game_model.notification = None

            self.renderer.render_game(self.game_model, self.mock_screen)

            # Check background was drawn
            self.mock_screen.blit.assert_called_once_with(self.mock_assets.backgrounds.game_board, [0, 0])

            # Check discs were drawn
            mock_discs.assert_called_once_with(self.game_model, self.mock_screen)

            # Check buttons were drawn (2 buttons in our mock)
            self.assertEqual(mock_btn.call_count, 2)
            # Verify specific buttons were drawn
            mock_btn.assert_any_call(self.game_model, self.game_model.active_buttons[0], self.mock_screen)
            mock_btn.assert_any_call(self.game_model, self.game_model.active_buttons[1], self.mock_screen)

            # Check notification was not drawn
            mock_notif.assert_not_called()

            # Reset for test with notification
            self.mock_screen.blit.reset_mock()
            mock_discs.reset_mock()
            mock_btn.reset_mock()

            # With notification
            self.game_model.notification = GameNotification.VICTORY

            self.renderer.render_game(self.game_model, self.mock_screen)

            # Check notification was drawn
            mock_notif.assert_called_once_with(self.game_model, self.mock_screen)


if __name__ == '__main__':
    unittest.main()