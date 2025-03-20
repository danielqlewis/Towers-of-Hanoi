import sys
import os
from pathlib import Path

# Add the parent directory (project root) to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

import unittest
import pygame
import logging
from unittest.mock import Mock, patch, MagicMock, call
from src.constants import ProgramState, ButtonFlag, MenuState, GameNotification, UserInput, MenuTheme
from src.models.menu_model import MenuModel
from src.models.game_model import GameModel
from src.models.button_entity import ButtonEntity
from src.controllers.controller import ProgramController
from src.controllers.program_loop import ProgramLoop


class TestProgramController(unittest.TestCase):
    def setUp(self):
        """Set up a fresh controller instance and mocked models before each test."""
        # Create mock models
        self.menu_model = Mock(spec=MenuModel)
        self.menu_model.notification = None
        self.menu_model.highlighted_button = None
        self.menu_model.active_buttons = []
        self.menu_model.current_menu = MenuState.MAIN

        self.game_model = Mock(spec=GameModel)
        self.game_model.notification = None
        self.game_model.highlighted_button = None
        self.game_model.active_buttons = []
        self.game_model.selected_tower = None
        self.game_model.towers = [[], [], []]

        # Create controller with menu model
        self.controller = ProgramController(self.menu_model)

    def test_init_state(self):
        """Test initial controller state."""
        self.assertEqual(self.controller.model, self.menu_model)
        self.assertFalse(self.controller.model_updated)
        self.assertIsNone(self.controller.next_state)
        self.assertFalse(self.controller.exit_flag)
        self.assertFalse(self.controller.asset_package_updated)
        self.assertFalse(self.controller.resolution_updated)

    def test_reset_settings_update_flags(self):
        """Test resetting the settings update flags."""
        self.controller.asset_package_updated = True
        self.controller.resolution_updated = True

        self.controller.reset_settings_update_flags()

        self.assertFalse(self.controller.asset_package_updated)
        self.assertFalse(self.controller.resolution_updated)

    def test_reset_render_flag(self):
        """Test resetting the render flag."""
        self.controller.model_updated = True

        self.controller.reset_render_flag()

        self.assertFalse(self.controller.model_updated)

    def test_update_state(self):
        """Test updating to a new model state."""
        self.controller.update_state(self.game_model)

        self.assertEqual(self.controller.model, self.game_model)
        self.assertIsNone(self.controller.next_state)
        self.assertTrue(self.controller.model_updated)

    def test_should_update_highlight_menu(self):
        """Test highlight updating check for menu state."""
        result = self.controller._should_update_highlight(ProgramState.MENU)
        self.assertTrue(result)

    def test_should_update_highlight_game_no_notification(self):
        """Test highlight updating check for game state with no notification."""
        self.controller.model = self.game_model
        self.game_model.notification = None

        result = self.controller._should_update_highlight(ProgramState.GAME)
        self.assertTrue(result)

    def test_should_update_highlight_game_with_notification(self):
        """Test highlight updating check for game state with notification."""
        self.controller.model = self.game_model
        self.game_model.notification = GameNotification.ILLEGAL_MOVE

        result = self.controller._should_update_highlight(ProgramState.GAME)
        self.assertFalse(result)

    def test_update_highlight_no_previous_highlight(self):
        """Test updating highlight when no button was previously highlighted."""
        # Create a mock button
        mock_button = Mock(spec=ButtonEntity)
        mock_button.flag = ButtonFlag.PLAY
        mock_button.rect = Mock()
        mock_button.rect.collidepoint.return_value = True

        # Set up model
        self.menu_model.highlighted_button = None
        self.menu_model.active_buttons = [mock_button]

        # Test
        self.controller._update_highlight((100, 100))

        # Verify
        self.menu_model.set_highlight.assert_called_once_with(ButtonFlag.PLAY)
        self.assertTrue(self.controller.model_updated)

    def test_update_highlight_previous_highlight_moved_away(self):
        """Test updating highlight when cursor moves away from highlighted button."""
        # Create a mock highlighted button
        mock_highlight = Mock(spec=ButtonEntity)
        mock_highlight.rect = Mock()
        mock_highlight.rect.collidepoint.return_value = False

        # Set up model
        self.menu_model.highlighted_button = mock_highlight

        # Test
        self.controller._update_highlight((100, 100))

        # Verify
        self.menu_model.clear_highlight.assert_called_once()
        self.assertTrue(self.controller.model_updated)

    def test_handle_start_gameplay(self):
        """Test handling the start gameplay action."""
        self.controller._handle_start_gameplay()
        self.assertEqual(self.controller.next_state, ProgramState.GAME)

    def test_handle_enter_options(self):
        """Test handling the enter options action."""
        self.controller._handle_enter_options()

        self.menu_model.reset_displayed_settings.assert_called_once()
        self.menu_model.update_menu_state.assert_called_once_with(MenuState.OPTIONS)

    def test_handle_program_exit(self):
        """Test handling the program exit action."""
        self.controller._handle_program_exit()
        self.assertTrue(self.controller.exit_flag)

    def test_handle_accept_options_no_changes(self):
        """Test accepting options with no changes."""
        # Setup model with same current and displayed settings
        self.menu_model.settings = {"theme": 1, "resolution": (960, 640)}
        self.menu_model.settings_select_display = [1, (960, 640)]

        self.controller._handle_accept_options()

        self.assertFalse(self.controller.asset_package_updated)
        self.assertFalse(self.controller.resolution_updated)
        self.menu_model.implement_displayed_settings.assert_called_once()
        self.menu_model.update_menu_state.assert_called_once_with(MenuState.MAIN)

    def test_handle_accept_options_with_changes(self):
        """Test accepting options with theme and resolution changes."""
        # Setup model with different theme and resolution
        self.menu_model.settings = {"theme": 1, "resolution": (960, 640)}
        self.menu_model.settings_select_display = [2, (1080, 720)]

        self.controller._handle_accept_options()

        self.assertTrue(self.controller.asset_package_updated)
        self.assertTrue(self.controller.resolution_updated)
        self.menu_model.implement_displayed_settings.assert_called_once()
        self.menu_model.update_menu_state.assert_called_once_with(MenuState.MAIN)

    def test_resolve_menu_click_credits(self):
        """Test resolving a menu click when in credits screen."""
        self.menu_model.current_menu = MenuState.CREDITS

        self.controller._resolve_menu_click()

        self.assertTrue(self.controller.model_updated)
        self.menu_model.update_menu_state.assert_called_once_with(MenuState.MAIN)

    def test_resolve_menu_click_tutorial_not_last_slide(self):
        """Test resolving a menu click when in tutorial screen (not last slide)."""
        self.menu_model.current_menu = MenuState.TUTORIAL
        self.menu_model.tutorial_step.return_value = False  # Not last slide

        self.controller._resolve_menu_click()

        self.assertTrue(self.controller.model_updated)
        self.menu_model.tutorial_step.assert_called_once()
        self.menu_model.update_menu_state.assert_not_called()

    def test_resolve_menu_click_tutorial_last_slide(self):
        """Test resolving a menu click when in tutorial screen (last slide)."""
        self.menu_model.current_menu = MenuState.TUTORIAL
        self.menu_model.tutorial_step.return_value = True  # Last slide

        self.controller._resolve_menu_click()

        self.assertTrue(self.controller.model_updated)
        self.menu_model.tutorial_step.assert_called_once()
        self.menu_model.update_menu_state.assert_called_once_with(MenuState.MAIN)

    def test_resolve_menu_click_with_highlighted_button(self):
        """Test resolving a menu click with a highlighted button."""
        # Create a mock highlighted button
        mock_highlight = Mock(spec=ButtonEntity)
        mock_highlight.flag = ButtonFlag.PLAY

        # Set up model
        self.menu_model.current_menu = MenuState.MAIN
        self.menu_model.highlighted_button = mock_highlight

        # Test
        self.controller._resolve_menu_click()

        # Verify
        self.assertTrue(self.controller.model_updated)
        self.assertEqual(self.controller.next_state, ProgramState.GAME)

    def test_resolve_notification_victory(self):
        """Test resolving a victory notification."""
        self.controller.model = self.game_model
        self.game_model.notification = GameNotification.VICTORY

        self.controller._resolve_notification()

        self.assertEqual(self.controller.next_state, ProgramState.MENU)

    def test_resolve_notification_illegal_move(self):
        """Test resolving an illegal move notification."""
        self.controller.model = self.game_model
        self.game_model.notification = GameNotification.ILLEGAL_MOVE

        self.controller._resolve_notification()

        self.game_model.clear_notification.assert_called_once()
        self.assertTrue(self.controller.model_updated)

    def test_handle_game_button_click_back_to_main(self):
        """Test handling a back to main button click in game."""
        self.controller.model = self.game_model

        # Create a mock highlighted button
        mock_highlight = Mock(spec=ButtonEntity)
        mock_highlight.flag = ButtonFlag.BACK_TO_MAIN
        self.game_model.highlighted_button = mock_highlight

        self.controller._handle_game_button_click()

        self.assertTrue(self.controller.model_updated)
        self.assertEqual(self.controller.next_state, ProgramState.MENU)

    def test_handle_game_button_click_reset_board(self):
        """Test handling a reset board button click in game."""
        self.controller.model = self.game_model

        # Create a mock highlighted button
        mock_highlight = Mock(spec=ButtonEntity)
        mock_highlight.flag = ButtonFlag.RESET_BOARD
        self.game_model.highlighted_button = mock_highlight

        self.controller._handle_game_button_click()

        self.assertTrue(self.controller.model_updated)
        self.game_model.reset_board.assert_called_once()

    def test_find_clicked_tower(self):
        """Test finding the clicked tower based on position."""
        # Test left tower
        self.assertEqual(self.controller._find_clicked_tower((100, 100)), 0)

        # Test middle tower
        self.assertEqual(self.controller._find_clicked_tower((400, 100)), 1)

        # Test right tower
        self.assertEqual(self.controller._find_clicked_tower((700, 100)), 2)

    def test_attempt_tower_select_empty(self):
        """Test attempting to select an empty tower."""
        self.controller.model = self.game_model
        self.game_model.towers = [[], [], []]

        self.controller._attempt_tower_select(0)

        self.game_model.set_selected_tower.assert_not_called()
        self.assertFalse(self.controller.model_updated)

    def test_attempt_tower_select_with_discs(self):
        """Test attempting to select a tower with discs."""
        self.controller.model = self.game_model
        self.game_model.towers = [[1], [], []]

        self.controller._attempt_tower_select(0)

        self.game_model.set_selected_tower.assert_called_once_with(0)
        self.assertTrue(self.controller.model_updated)

    def test_execute_move_normal(self):
        """Test executing a move between towers."""
        self.controller.model = self.game_model
        self.game_model.selected_tower = 0
        self.game_model.is_complete.return_value = False

        self.controller._execute_move(1)

        self.game_model.move_disc.assert_called_once_with(0, 1)
        self.game_model.set_selected_tower.assert_called_once_with(None)
        self.game_model.set_notification.assert_not_called()

    def test_execute_move_victory(self):
        """Test executing a move that completes the game."""
        self.controller.model = self.game_model
        self.game_model.selected_tower = 0
        self.game_model.is_complete.return_value = True

        self.controller._execute_move(1)

        self.game_model.move_disc.assert_called_once_with(0, 1)
        self.game_model.set_selected_tower.assert_called_once_with(None)
        self.game_model.set_notification.assert_called_once_with(GameNotification.VICTORY)

    def test_handle_second_tower_click_deselect(self):
        """Test deselecting a tower by clicking it again."""
        self.controller.model = self.game_model
        self.game_model.selected_tower = 0

        self.controller._handle_second_tower_click(0)

        self.game_model.set_selected_tower.assert_called_once_with(None)
        self.game_model.check_move_legal.assert_not_called()

    def test_handle_second_tower_click_legal_move(self):
        """Test handling a legal move between towers."""
        self.controller.model = self.game_model
        self.game_model.selected_tower = 0
        self.game_model.check_move_legal.return_value = True

        with patch.object(self.controller, '_execute_move') as mock_execute:
            self.controller._handle_second_tower_click(1)

            self.game_model.check_move_legal.assert_called_once_with(0, 1)
            mock_execute.assert_called_once_with(1)

    def test_handle_second_tower_click_illegal_move(self):
        """Test handling an illegal move between towers."""
        self.controller.model = self.game_model
        self.game_model.selected_tower = 0
        self.game_model.check_move_legal.return_value = False

        self.controller._handle_second_tower_click(1)

        self.game_model.check_move_legal.assert_called_once_with(0, 1)
        self.game_model.set_notification.assert_called_once_with(GameNotification.ILLEGAL_MOVE)

    def test_handle_tower_interaction_first_click(self):
        """Test handling the first click on a tower."""
        self.controller.model = self.game_model
        self.game_model.selected_tower = None

        with patch.object(self.controller, '_attempt_tower_select') as mock_attempt:
            self.controller._handle_tower_interaction(0)

            mock_attempt.assert_called_once_with(0)

    def test_handle_tower_interaction_second_click(self):
        """Test handling the second click with a tower already selected."""
        self.controller.model = self.game_model
        self.game_model.selected_tower = 0

        with patch.object(self.controller, '_handle_second_tower_click') as mock_handle:
            self.controller._handle_tower_interaction(1)

            self.assertTrue(self.controller.model_updated)
            mock_handle.assert_called_once_with(1)

    def test_resolve_gameboard_click_with_notification(self):
        """Test resolving a gameboard click with an active notification."""
        self.controller.model = self.game_model
        self.game_model.notification = GameNotification.ILLEGAL_MOVE

        with patch.object(self.controller, '_resolve_notification') as mock_resolve:
            self.controller._resolve_gameboard_click((100, 100))

            mock_resolve.assert_called_once()

    def test_resolve_gameboard_click_with_highlighted_button(self):
        """Test resolving a gameboard click with a highlighted button."""
        self.controller.model = self.game_model
        self.game_model.notification = None
        self.game_model.highlighted_button = Mock(spec=ButtonEntity)

        with patch.object(self.controller, '_handle_game_button_click') as mock_handle:
            self.controller._resolve_gameboard_click((100, 100))

            mock_handle.assert_called_once()

    def test_resolve_gameboard_click_tower_interaction(self):
        """Test resolving a gameboard click on a tower."""
        self.controller.model = self.game_model
        self.game_model.notification = None
        self.game_model.highlighted_button = None

        with patch.object(self.controller, '_find_clicked_tower') as mock_find, \
                patch.object(self.controller, '_handle_tower_interaction') as mock_handle:
            mock_find.return_value = 1

            self.controller._resolve_gameboard_click((400, 100))

            mock_find.assert_called_once_with((400, 100))
            mock_handle.assert_called_once_with(1)

    def test_handle_input_menu_click(self):
        """Test handling a mouse click in menu state."""
        user_input = UserInput(position=(100, 100), clicked=True)

        with patch.object(self.controller, '_update_highlight') as mock_highlight, \
                patch.object(self.controller, '_resolve_menu_click') as mock_resolve:
            self.controller.handle_input(user_input, ProgramState.MENU)

            mock_highlight.assert_called_once_with((100, 100))
            mock_resolve.assert_called_once()

    def test_handle_input_game_click(self):
        """Test handling a mouse click in game state."""
        user_input = UserInput(position=(100, 100), clicked=True)

        # Switch to game model
        self.controller.model = self.game_model

        with patch.object(self.controller, '_update_highlight') as mock_highlight, \
                patch.object(self.controller, '_resolve_gameboard_click') as mock_resolve:
            self.controller.handle_input(user_input, ProgramState.GAME)

            mock_highlight.assert_called_once_with((100, 100))
            mock_resolve.assert_called_once_with((100, 100))

    def test_handle_input_mouse_move(self):
        """Test handling mouse movement without click."""
        user_input = UserInput(position=(100, 100), clicked=False)

        with patch.object(self.controller, '_update_highlight') as mock_highlight, \
                patch.object(self.controller, '_resolve_menu_click') as mock_resolve:
            self.controller.handle_input(user_input, ProgramState.MENU)

            mock_highlight.assert_called_once_with((100, 100))
            mock_resolve.assert_not_called()


class TestGameLoop(unittest.TestCase):
    @patch('pygame.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.Surface')
    @patch('src.views.assets.build_asset_container')
    @patch('src.controllers.program_loop.GameRenderer')
    @patch('src.controllers.program_loop.ProgramController')
    @patch('pygame.time.Clock')
    @patch('pygame.display.set_caption')
    def setUp(self, mock_set_caption, mock_clock, mock_controller_class, mock_renderer_class,
              mock_build_assets, mock_surface, mock_set_mode, mock_init):
        """Set up a fresh GameLoop instance with all pygame dependencies mocked."""
        # Set up mocks
        self.mock_screen = MagicMock()
        mock_set_mode.return_value = self.mock_screen

        self.mock_virtual_screen = MagicMock()
        mock_surface.return_value = self.mock_virtual_screen

        self.mock_assets = MagicMock()
        mock_build_assets.return_value = self.mock_assets

        self.mock_renderer = MagicMock()
        mock_renderer_class.return_value = self.mock_renderer

        self.mock_controller = MagicMock()
        mock_controller_class.return_value = self.mock_controller
        self.mock_controller.exit_flag = False
        self.mock_controller.model_updated = False
        self.mock_controller.next_state = None

        self.mock_clock = MagicMock()
        mock_clock.return_value = self.mock_clock

        # Create the GameLoop instance
        self.game_loop = ProgramLoop()

        # Store mock classes for assertions
        self.mock_renderer_class = mock_renderer_class
        self.mock_controller_class = mock_controller_class
        self.mock_build_assets = mock_build_assets

    @patch('pygame.quit')
    @patch('sys.exit')
    def test_init_failure(self, mock_exit, mock_quit):
        """Test handling of initialization failure."""
        # Setup pygame.init to raise an error
        with patch('pygame.init', side_effect=pygame.error("Test error")):
            # This should log an error and exit
            with patch('src.controllers.program_loop.logger.error') as mock_logger:
                with self.assertRaises(SystemExit):
                    ProgramLoop()

                mock_logger.assert_called_once()
                mock_quit.assert_not_called()  # pygame.quit not called because init failed
                mock_exit.assert_called_once_with(1)

    @patch('sys.exit')
    def test_init_asset_failure(self, mock_exit):
        """Test handling of asset loading failure."""
        # Setup build_asset_container to return None (failed)
        with patch('src.views.assets.build_asset_container', return_value=None):
            with patch('pygame.quit') as mock_quit:
                with patch('builtins.print') as mock_print:
                    with self.assertRaises(SystemExit):
                        ProgramLoop()

                    mock_print.assert_called_once_with("Failed to load assets")
                    mock_quit.assert_called_once()
                    mock_exit.assert_called_once_with(1)

    def test_init_success(self):
        """Test successful initialization."""
        # Verify components were initialized correctly
        self.assertEqual(self.game_loop.current_state, ProgramState.MENU)
        self.assertTrue(self.game_loop.running)
        self.assertEqual(self.game_loop.VIRTUAL_SCREEN_SIZE, (960, 640))

        # Verify appropriate objects were created
        self.assertIsInstance(self.game_loop.menu_model, MenuModel)
        self.assertEqual(self.game_loop.renderer, self.mock_renderer)
        self.assertEqual(self.game_loop.controller, self.mock_controller)

        # Verify initialization calls
        self.mock_build_assets.assert_called_once_with(MenuTheme.STANDARD)
        self.mock_renderer_class.assert_called_once_with(self.mock_assets)
        self.mock_controller_class.assert_called_once()

    def test_check_for_exit_events_no_quit(self):
        """Test checking for exit events with no quit event."""
        # Create mock events without quit
        mock_events = [
            Mock(type=pygame.MOUSEMOTION),
            Mock(type=pygame.MOUSEBUTTONDOWN)
        ]

        result = ProgramLoop._check_for_exit_events(mock_events)
        self.assertFalse(result)

    def test_check_for_exit_events_with_quit(self):
        """Test checking for exit events with a quit event."""
        # Create mock events including a quit
        mock_events = [
            Mock(type=pygame.MOUSEMOTION),
            Mock(type=pygame.QUIT),
            Mock(type=pygame.MOUSEBUTTONDOWN)
        ]

        result = ProgramLoop._check_for_exit_events(mock_events)
        self.assertTrue(result)

    @patch('pygame.mouse.get_pos')
    def test_process_input_no_click(self, mock_get_pos):
        """Test input processing without a click."""
        # Setup mouse position
        mock_get_pos.return_value = (480, 320)

        # Ensure screen size matches virtual size to avoid scaling calculations
        self.mock_screen.get_size.return_value = self.game_loop.VIRTUAL_SCREEN_SIZE

        # Create mock events without click
        mock_events = [Mock(type=pygame.MOUSEMOTION)]

        result = self.game_loop.process_input(mock_events)

        self.assertEqual(result.position, (480, 320))
        self.assertFalse(result.clicked)

    @patch('pygame.mouse.get_pos')
    def test_process_input_with_click(self, mock_get_pos):
        """Test input processing with a click."""
        # Setup mouse position
        mock_get_pos.return_value = (480, 320)

        # Create mock events with click
        mock_events = [
            Mock(type=pygame.MOUSEMOTION),
            Mock(type=pygame.MOUSEBUTTONDOWN)
        ]

        result = self.game_loop.process_input(mock_events)

        self.assertEqual(result.position, (480, 320))
        self.assertTrue(result.clicked)

    @patch('pygame.mouse.get_pos')
    def test_process_input_with_scaling(self, mock_get_pos):
        """Test input scaling when screen size differs from virtual size."""
        # Setup mouse position
        mock_get_pos.return_value = (960, 640)

        # Set screen size to be twice the virtual size
        self.mock_screen.get_size.return_value = (1920, 1280)

        # Create mock events
        mock_events = [Mock(type=pygame.MOUSEMOTION)]

        result = self.game_loop.process_input(mock_events)

        # Position should be scaled to virtual coordinates
        self.assertEqual(result.position, (480, 320))
        self.assertFalse(result.clicked)

    @patch('pygame.event.get')
    def test_handle_user_input_no_exit(self, mock_event_get):
        """Test handling user input with no exit event."""
        # Setup mock events
        mock_events = [Mock(type=pygame.MOUSEMOTION)]
        mock_event_get.return_value = mock_events

        # Setup controller to not exit
        self.mock_controller.exit_flag = False

        with patch.object(self.game_loop, 'process_input', return_value=UserInput((100, 100), False)) as mock_process:
            result = self.game_loop.handle_user_input()

            # Should continue running
            self.assertTrue(result)

            # Should process events and input
            mock_event_get.assert_called_once()
            mock_process.assert_called_once_with(mock_events)

            # Should pass input to controller
            self.mock_controller.handle_input.assert_called_once()

    @patch('pygame.event.get')
    def test_handle_user_input_with_exit_event(self, mock_event_get):
        """Test handling user input with an exit event."""
        # Setup mock events with quit
        mock_events = [Mock(type=pygame.QUIT)]
        mock_event_get.return_value = mock_events

        result = self.game_loop.handle_user_input()

        # Should signal to stop running
        self.assertFalse(result)

        # Should not process input further once exit is detected
        self.mock_controller.handle_input.assert_not_called()

    @patch('pygame.event.get')
    def test_handle_user_input_controller_exit(self, mock_event_get):
        """Test handling user input when controller signals exit."""
        # Setup mock events
        mock_events = [Mock(type=pygame.MOUSEMOTION)]
        mock_event_get.return_value = mock_events

        # Setup controller to exit
        self.mock_controller.exit_flag = True

        result = self.game_loop.handle_user_input()

        # Should signal to stop running
        self.assertFalse(result)

    def test_check_and_update_settings_no_changes(self):
        """Test settings update check with no changes."""
        # Setup no setting changes
        self.mock_controller.asset_package_updated = False
        self.mock_controller.resolution_updated = False

        self.game_loop.check_and_update_settings()

        # Should reset flags but not update anything
        self.mock_controller.reset_settings_update_flags.assert_called_once()
        self.mock_build_assets.assert_called_once()  # Only from initialization

    @patch('src.views.assets.build_asset_container')
    @patch('pygame.display.set_mode')
    def test_check_and_update_settings_with_changes(self, mock_set_mode, mock_build_assets):
        """Test settings update with theme and resolution changes."""
        # Setup theme change
        self.mock_controller.asset_package_updated = True
        self.mock_controller.resolution_updated = True

        # Setup model settings
        mock_model = MagicMock()
        mock_model.settings = {
            "theme": MenuTheme.RED,
            "resolution": (1080, 720)
        }
        self.mock_controller.model = mock_model

        # Setup asset creation
        mock_assets = MagicMock()
        mock_build_assets.return_value = mock_assets

        # Run the method
        self.game_loop.check_and_update_settings()

        # Verify new assets were created with the correct theme
        mock_build_assets.assert_called_with(MenuTheme.RED)

        # Verify renderer was updated
        self.assertIsInstance(self.game_loop.renderer, MagicMock)

        # Verify screen resolution was updated
        mock_set_mode.assert_called_once_with((1080, 720))

        # Verify flags were reset
        self.mock_controller.reset_settings_update_flags.assert_called_once()

    def test_handle_program_state_change_no_change(self):
        """Test state change handling with no pending change."""
        # Setup no state change
        self.mock_controller.next_state = None

        self.game_loop.handle_program_state_change()

        # Should not update state or model
        self.mock_controller.update_state.assert_not_called()
        self.assertEqual(self.game_loop.current_state, ProgramState.MENU)

    def test_handle_program_state_change_to_game(self):
        """Test state change from menu to game."""
        # Setup state change to game
        self.mock_controller.next_state = ProgramState.GAME

        # Setup model with difficulty setting
        mock_model = MagicMock()
        mock_model.settings = {"difficulty": 4}
        self.mock_controller.model = mock_model

        # Run the method
        with patch('src.controllers.program_loop.GameModel') as mock_game_model_class:
            mock_game_model = MagicMock()
            mock_game_model_class.return_value = mock_game_model

            self.game_loop.handle_program_state_change()

            # Verify state was updated
            self.assertEqual(self.game_loop.current_state, ProgramState.GAME)

            # Verify new game model was created with correct difficulty
            mock_game_model_class.assert_called_once_with(4)

            # Verify controller was updated with new model
            self.mock_controller.update_state.assert_called_once_with(mock_game_model)

    def test_handle_program_state_change_to_menu(self):
        """Test state change from game to menu."""
        # Setup game state first
        self.game_loop.current_state = ProgramState.GAME

        # Setup state change to menu
        self.mock_controller.next_state = ProgramState.MENU

        # Run the method
        self.game_loop.handle_program_state_change()

        # Verify state was updated
        self.assertEqual(self.game_loop.current_state, ProgramState.MENU)

        # Verify controller was updated with menu model
        self.mock_controller.update_state.assert_called_once_with(self.game_loop.menu_model)

    def test_update_and_render_no_update(self):
        """Test rendering when no update is needed."""
        # Setup no model update
        self.mock_controller.model_updated = False

        self.game_loop.update_and_render()

        # Should not render or flip display
        self.mock_renderer.render_menu.assert_not_called()
        self.mock_renderer.render_game.assert_not_called()

    @patch('pygame.transform.smoothscale')
    @patch('pygame.display.flip')
    def test_update_and_render_menu_state(self, mock_flip, mock_smoothscale):
        """Test rendering in menu state."""
        # Setup model update in menu state
        self.mock_controller.model_updated = True
        self.game_loop.current_state = ProgramState.MENU

        # Setup scaling
        mock_scaled = MagicMock()
        mock_smoothscale.return_value = mock_scaled

        self.game_loop.update_and_render()

        # Verify menu was rendered
        self.mock_renderer.render_menu.assert_called_once_with(self.mock_controller.model, self.mock_virtual_screen)
        self.mock_renderer.render_game.assert_not_called()

        # Verify display update
        mock_smoothscale.assert_called_once()
        self.mock_screen.blit.assert_called_once_with(mock_scaled, (0, 0))
        mock_flip.assert_called_once()

        # Verify render flag was reset
        self.mock_controller.reset_render_flag.assert_called_once()

    @patch('pygame.transform.smoothscale')
    @patch('pygame.display.flip')
    def test_update_and_render_game_state(self, mock_flip, mock_smoothscale):
        """Test rendering in game state."""
        # Setup model update in game state
        self.mock_controller.model_updated = True
        self.game_loop.current_state = ProgramState.GAME

        # Setup scaling
        mock_scaled = MagicMock()
        mock_smoothscale.return_value = mock_scaled

        self.game_loop.update_and_render()

        # Verify game was rendered
        self.mock_renderer.render_game.assert_called_once_with(self.mock_controller.model, self.mock_virtual_screen)
        self.mock_renderer.render_menu.assert_not_called()

        # Verify display update
        mock_smoothscale.assert_called_once()
        self.mock_screen.blit.assert_called_once_with(mock_scaled, (0, 0))
        mock_flip.assert_called_once()

        # Verify render flag was reset
        self.mock_controller.reset_render_flag.assert_called_once()

    @patch('pygame.quit')
    def test_run_program_immediate_exit(self, mock_quit):
        """Test running the program with immediate exit."""
        # Setup to exit immediately after first loop
        with patch.object(self.game_loop, 'handle_user_input', return_value=False) as mock_handle_input, \
                patch.object(self.game_loop, 'check_and_update_settings') as mock_check_settings, \
                patch.object(self.game_loop, 'handle_program_state_change') as mock_handle_state, \
                patch.object(self.game_loop, 'update_and_render') as mock_update_render:
            self.game_loop.run_program()

            # Verify initial render happened
            self.assertTrue(self.mock_controller.model_updated)
            self.assertEqual(mock_update_render.call_count, 2)  # Initial + one loop

            # Verify main loop components were called
            mock_handle_input.assert_called_once()
            mock_check_settings.assert_called_once()
            mock_handle_state.assert_called_once()

            # Verify program was exited
            mock_quit.assert_called_once()

    @patch('pygame.quit')
    def test_run_program_with_multiple_iterations(self, mock_quit):
        """Test running the program with multiple iterations before exit."""
        # Setup to run for 3 iterations then exit
        handle_input_mock = MagicMock(side_effect=[True, True, False])

        with patch.object(self.game_loop, 'handle_user_input', handle_input_mock), \
                patch.object(self.game_loop, 'check_and_update_settings') as mock_check_settings, \
                patch.object(self.game_loop, 'handle_program_state_change') as mock_handle_state, \
                patch.object(self.game_loop, 'update_and_render') as mock_update_render:
            self.game_loop.run_program()

            # Verify the loop ran the expected number of times
            self.assertEqual(handle_input_mock.call_count, 3)
            self.assertEqual(mock_check_settings.call_count, 3)
            self.assertEqual(mock_handle_state.call_count, 3)
            self.assertEqual(mock_update_render.call_count, 4)  # Initial + three loops

            # Verify program was exited
            mock_quit.assert_called_once()

            # Verify the clock ticked for each iteration
            self.assertEqual(self.mock_clock.tick.call_count, 3)
            for call_args in self.mock_clock.tick.call_args_list:
                self.assertEqual(call_args, call(60))  # FPS of 60


if __name__ == '__main__':
    unittest.main()
