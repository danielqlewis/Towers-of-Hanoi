import unittest
from unittest.mock import Mock, patch
from src.constants import ButtonFlag, GameNotification, MenuState, MenuTheme
from src.models.game_model import GameModel
from src.models.menu_model import MenuModel


# We'll add imports for the tower model after you share it


class TestGameModel(unittest.TestCase):
    def setUp(self):
        """Set up a fresh GameModel instance before each test."""
        self.game = GameModel(disc_num=3)

    def test_init_default(self):
        """Test that the GameModel initializes correctly with default values."""
        game = GameModel()
        self.assertEqual(game.towers, ([2, 1, 0], [], []))
        self.assertIsNone(game.highlighted_button)
        self.assertIsNone(game.selected_tower)
        self.assertIsNone(game.notification)
        self.assertIn(ButtonFlag.RESET_BOARD, [btn.flag for btn in game.active_buttons])
        self.assertIn(ButtonFlag.BACK_TO_MAIN, [btn.flag for btn in game.active_buttons])

    def test_init_custom_discs(self):
        """Test initialization with a custom number of discs."""
        game = GameModel(disc_num=5)
        self.assertEqual(game.towers, ([4, 3, 2, 1, 0], [], []))

    def test_check_move_legal(self):
        """Test the move legality checker with various scenarios."""
        # Test moving from empty tower (illegal)
        self.assertFalse(self.game.check_move_legal(1, 2))

        # Test moving to empty tower (legal)
        self.assertTrue(self.game.check_move_legal(0, 1))

        # Set up a scenario with discs on multiple towers
        self.game.towers = ([2, 1], [0], [])

        # Test smaller disc onto larger disc (legal)
        self.assertTrue(self.game.check_move_legal(1, 0))

        # Test larger disc onto smaller disc (illegal)
        self.assertFalse(self.game.check_move_legal(0, 1))

    def test_move_disc(self):
        """Test that discs move correctly between towers."""
        # Move a disc from tower 0 to tower 1
        self.game.move_disc(0, 1)
        self.assertEqual(self.game.towers, ([2, 1], [0], []))

        # Move another disc
        self.game.move_disc(0, 2)
        self.assertEqual(self.game.towers, ([2], [0], [1]))

    def test_is_complete(self):
        """Test the game completion checker."""
        # Game starts incomplete
        self.assertFalse(self.game.is_complete())

        # Move all discs to tower 2 (complete)
        self.game.towers = ([], [], [2, 1, 0])
        self.assertTrue(self.game.is_complete())

        # Discs on tower 1 (incomplete)
        self.game.towers = ([], [1, 0], [2])
        self.assertFalse(self.game.is_complete())

    def test_reset_board(self):
        """Test that the board resets properly."""
        # First move some discs
        self.game.towers = ([2], [1], [0])
        self.game.selected_tower = 1

        # Reset and check
        self.game.reset_board()
        self.assertEqual(self.game.towers, ([2, 1, 0], [], []))
        self.assertIsNone(self.game.selected_tower)

    def test_set_selected_tower(self):
        """Test setting the selected tower."""
        self.assertIsNone(self.game.selected_tower)
        self.game.set_selected_tower(1)
        self.assertEqual(self.game.selected_tower, 1)
        self.game.set_selected_tower(None)
        self.assertIsNone(self.game.selected_tower)

    def test_notification_methods(self):
        """Test setting and clearing notifications."""
        self.assertIsNone(self.game.notification)

        # Set notification
        test_notification = GameNotification.ILLEGAL_MOVE
        self.game.set_notification(test_notification)
        self.assertEqual(self.game.notification, test_notification)

        # Clear notification
        self.game.clear_notification()
        self.assertIsNone(self.game.notification)

    def test_highlight_methods(self):
        """Test setting and clearing button highlights."""
        self.assertIsNone(self.game.highlighted_button)

        # Set highlight
        test_highlight = ButtonFlag.RESET_BOARD
        self.game.set_highlight(test_highlight)
        self.assertEqual(self.game.highlighted_button.flag, test_highlight)

        # Clear highlight
        self.game.clear_highlight()
        self.assertIsNone(self.game.highlighted_button)


class TestMenuModel(unittest.TestCase):
    def setUp(self):
        """Set up a fresh MenuModel instance before each test."""
        self.menu = MenuModel()

    def test_init(self):
        """Test that the MenuModel initializes correctly."""
        self.assertEqual(self.menu.settings["theme"], MenuTheme.STANDARD)
        self.assertEqual(self.menu.settings["resolution"], (960, 640))
        self.assertEqual(self.menu.settings["difficulty"], 3)
        self.assertEqual(self.menu.current_menu, MenuState.MAIN)
        self.assertEqual(self.menu.tutorial_slide, 0)
        self.assertEqual(self.menu.total_tutorial_slides, 8)
        self.assertIsNone(self.menu.highlighted_button)

        # Check that the active buttons are correct for the main menu
        button_flags = [btn.flag for btn in self.menu.active_buttons]
        for btn in MenuModel.main_menu_buttons:
            self.assertIn(btn, button_flags)

    def test_update_menu_state(self):
        """Test that updating the menu state changes active buttons."""
        # Test changing to options menu
        self.menu.update_menu_state(MenuState.OPTIONS)
        self.assertEqual(self.menu.current_menu, MenuState.OPTIONS)

        # Verify options menu buttons
        option_button_flags = [btn.flag for btn in self.menu.active_buttons]
        for btn in MenuModel.option_menu_buttons:
            self.assertIn(btn, option_button_flags)

        # Test changing to a menu with no buttons
        self.menu.update_menu_state(MenuState.TUTORIAL)
        self.assertEqual(self.menu.current_menu, MenuState.TUTORIAL)
        self.assertEqual(len(self.menu.active_buttons), 0)

    def test_highlight_methods(self):
        """Test setting and clearing button highlights."""
        self.assertIsNone(self.menu.highlighted_button)

        # Set highlight
        test_highlight = ButtonFlag.PLAY
        self.menu.set_highlight(test_highlight)
        self.assertEqual(self.menu.highlighted_button.flag, test_highlight)

        # Clear highlight
        self.menu.clear_highlight()
        self.assertIsNone(self.menu.highlighted_button)

    def test_tutorial_step(self):
        """Test tutorial slide navigation."""
        # Initially at slide 0
        self.assertEqual(self.menu.tutorial_slide, 0)

        # Step through slides until before the last one
        for i in range(self.menu.total_tutorial_slides - 1):
            result = self.menu.tutorial_step()
            self.assertEqual(self.menu.tutorial_slide, i + 1)
            self.assertFalse(result)  # Not at the end yet

        # Last step should return True and reset to slide 0
        result = self.menu.tutorial_step()
        self.assertTrue(result)  # Reached the end
        self.assertEqual(self.menu.tutorial_slide, 0)  # Reset to beginning

    def test_cycle_theme_displayed(self):
        """Test cycling through available themes."""
        # Start with standard theme
        self.assertEqual(self.menu.settings_select_display[0], MenuTheme.STANDARD)

        # Cycle through all themes
        for _ in range(len(MenuTheme) - 1):
            self.menu.cycle_theme_displayed()
            # Not testing specific values, just that it changes

        # After cycling through all, should be back to STANDARD
        self.menu.cycle_theme_displayed()
        self.assertEqual(self.menu.settings_select_display[0], MenuTheme.STANDARD)

    def test_cycle_resolution_displayed(self):
        """Test cycling through available resolutions."""
        resolutions = [
            (720, 480),
            (864, 576),
            (960, 640),
            (1080, 720),
            (1296, 864)
        ]

        # Start with default resolution
        self.assertEqual(self.menu.settings_select_display[1], (960, 640))

        # Cycle and check each resolution
        for _ in range(len(resolutions) - 1):
            self.menu.cycle_resolution_displayed()
            self.assertIn(self.menu.settings_select_display[1], resolutions)

        # After cycling through all, should be back to the original
        self.menu.cycle_resolution_displayed()
        self.assertEqual(self.menu.settings_select_display[1], (960, 640))

    def test_cycle_difficulty_displayed(self):
        """Test cycling through available difficulties."""
        difficulties = [3, 4, 5]

        # Start with default difficulty
        self.assertEqual(self.menu.settings_select_display[2], 3)

        # Cycle through all difficulties
        self.menu.cycle_difficulty_displayed()
        self.assertEqual(self.menu.settings_select_display[2], 4)

        self.menu.cycle_difficulty_displayed()
        self.assertEqual(self.menu.settings_select_display[2], 5)

        # Cycle back to the beginning
        self.menu.cycle_difficulty_displayed()
        self.assertEqual(self.menu.settings_select_display[2], 3)

    def test_reset_displayed_settings(self):
        """Test resetting displayed settings to match current settings."""
        # Change displayed settings
        self.menu.settings_select_display = [MenuTheme(1), (720, 480), 5]

        # Reset and check
        self.menu.reset_displayed_settings()
        self.assertEqual(self.menu.settings_select_display[0], self.menu.settings["theme"])
        self.assertEqual(self.menu.settings_select_display[1], self.menu.settings["resolution"])
        self.assertEqual(self.menu.settings_select_display[2], self.menu.settings["difficulty"])

    def test_implement_displayed_settings(self):
        """Test implementing displayed settings to actual settings."""
        # Change displayed settings
        new_theme = MenuTheme(1)
        new_resolution = (1080, 720)
        new_difficulty = 5
        self.menu.settings_select_display = [new_theme, new_resolution, new_difficulty]

        # Implement and check
        self.menu.implement_displayed_settings()
        self.assertEqual(self.menu.settings["theme"], new_theme)
        self.assertEqual(self.menu.settings["resolution"], new_resolution)
        self.assertEqual(self.menu.settings["difficulty"], new_difficulty)