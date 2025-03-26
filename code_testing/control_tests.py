import sys
import os
from pathlib import Path
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


class TestProgramLoop(unittest.TestCase):
    """Basic tests for the ProgramLoop class."""

    def setUp(self):
        """Set up test environment with minimal mocking."""
        # Create patches for essential dependencies
        # 1. Patch pygame initialization
        self.pygame_init_patcher = patch('pygame.init')
        self.mock_pygame_init = self.pygame_init_patcher.start()
        self.mock_pygame_init.return_value = (0, 0)  # Success count, fail count

        # 2. Patch display functions
        self.set_mode_patcher = patch('pygame.display.set_mode')
        self.mock_set_mode = self.set_mode_patcher.start()
        self.mock_screen = Mock()
        self.mock_set_mode.return_value = self.mock_screen

        self.set_caption_patcher = patch('pygame.display.set_caption')
        self.mock_set_caption = self.set_caption_patcher.start()

        # 3. Patch Surface creation
        self.surface_patcher = patch('pygame.Surface')
        self.mock_surface = self.surface_patcher.start()
        self.mock_virtual_screen = Mock()
        self.mock_surface.return_value = self.mock_virtual_screen

        # 4. Patch asset loading - critical for initialization
        self.assets_patcher = patch('src.views.assets.build_asset_container')
        self.mock_assets = self.assets_patcher.start()
        self.mock_asset_container = Mock()
        self.mock_assets.return_value = self.mock_asset_container  # Return non-None value

        # 5. Patch renderer and controller creation
        self.renderer_patcher = patch('src.views.renderer.GameRenderer')
        self.mock_renderer_class = self.renderer_patcher.start()
        self.mock_renderer = Mock()
        self.mock_renderer_class.return_value = self.mock_renderer

        self.controller_patcher = patch('src.controllers.controller.ProgramController')
        self.mock_controller_class = self.controller_patcher.start()
        self.mock_controller = Mock()
        self.mock_controller_class.return_value = self.mock_controller

        # 6. Patch the clock
        self.clock_patcher = patch('pygame.time.Clock')
        self.mock_clock_class = self.clock_patcher.start()
        self.mock_clock = Mock()
        self.mock_clock_class.return_value = self.mock_clock

        # 7. Patch pygame.quit to prevent actual quitting
        self.quit_patcher = patch('pygame.quit')
        self.mock_quit = self.quit_patcher.start()

        # 8. Patch sys.exit to prevent test termination
        self.exit_patcher = patch('sys.exit')
        self.mock_exit = self.exit_patcher.start()

    def tearDown(self):
        """Clean up all patches."""
        # Stop all patches
        self.pygame_init_patcher.stop()
        self.set_mode_patcher.stop()
        self.set_caption_patcher.stop()
        self.surface_patcher.stop()
        self.assets_patcher.stop()
        self.renderer_patcher.stop()
        self.controller_patcher.stop()
        self.clock_patcher.stop()
        self.quit_patcher.stop()
        self.exit_patcher.stop()

    def test_initialization(self):
        """Test basic initialization of the ProgramLoop class."""
        # Create an instance of ProgramLoop
        program_loop = ProgramLoop()

        # Basic assertions about initialization
        self.assertEqual(program_loop.current_state, ProgramState.MENU)
        self.assertTrue(program_loop.running)
        self.mock_set_caption.assert_called_once_with("Towers of Hanoi")

    def test_check_for_exit_events(self):
        """Test the static method that checks for exit events."""
        # Test with no exit events
        mock_events = [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)]
        result = ProgramLoop._check_for_exit_events(mock_events)
        self.assertFalse(result)

        # Test with an exit event
        mock_events = [pygame.event.Event(pygame.QUIT)]
        result = ProgramLoop._check_for_exit_events(mock_events)
        self.assertTrue(result)

    def test_process_input_no_click(self):
        """Test processing input with mouse movement but no click."""
        # Create mouse position patch
        with patch('pygame.mouse.get_pos', return_value=(480, 320)):
            # Create an instance
            program_loop = ProgramLoop()

            # Mock the screen size
            program_loop.screen.get_size.return_value = (960, 640)

            # Create sample event list with no mouse clicks
            mock_events = [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)]

            # Process input
            result = program_loop.process_input(mock_events)

            # Verify results - mouse coordinates should match since screen size matches virtual
            self.assertEqual(result.position, (480, 320))
            self.assertFalse(result.clicked)

    def test_process_input_with_click(self):
        """Test processing input with mouse click."""
        # Create mouse position patch
        with patch('pygame.mouse.get_pos', return_value=(480, 320)):
            # Create an instance
            program_loop = ProgramLoop()

            # Mock the screen size
            program_loop.screen.get_size.return_value = (960, 640)

            # Create sample event list with mouse click
            mock_events = [pygame.event.Event(pygame.MOUSEBUTTONDOWN)]

            # Process input
            result = program_loop.process_input(mock_events)

            # Verify results
            self.assertEqual(result.position, (480, 320))
            self.assertTrue(result.clicked)

    def test_process_input_scaled_screen(self):
        """Test that input coordinates scale correctly with different screen sizes."""
        # Create mouse position patch
        with patch('pygame.mouse.get_pos', return_value=(960, 640)):
            # Create an instance
            program_loop = ProgramLoop()

            # Mock screen size to be double the virtual screen size
            program_loop.screen.get_size.return_value = (1920, 1280)

            # Process input (empty event list is fine)
            result = program_loop.process_input([])

            # Verify results - coordinates should be scaled down to virtual screen
            self.assertEqual(result.position, (480, 320))

    def test_handle_user_input_exit_event(self):
        """Test handling user input with exit event."""
        # Create an instance
        program_loop = ProgramLoop()

        # Set up mock for event.get to return an exit event
        with patch('pygame.event.get', return_value=[pygame.event.Event(pygame.QUIT)]):
            # Handle input
            result = program_loop.handle_user_input()

            # Verify results - should return False to stop the game loop
            self.assertFalse(result)
            # Controller should not be called since we're exiting
            self.mock_controller.handle_input.assert_not_called()

    def test_handle_user_input_normal(self):
        """Test handling normal user input."""
        # Create an instance
        program_loop = ProgramLoop()
        program_loop.controller = self.mock_controller
        self.mock_controller.exit_flag = False

        # Mock normal event
        mock_event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)

        # Set up mocks
        with patch('pygame.event.get', return_value=[mock_event]), \
                patch('pygame.mouse.get_pos', return_value=(100, 100)), \
                patch.object(ProgramLoop, 'process_input',
                             return_value=UserInput((100, 100), False)):
            # Handle input
            result = program_loop.handle_user_input()

            # Verify results
            self.assertTrue(result)
            self.mock_controller.handle_input.assert_called_once_with(
                UserInput((100, 100), False), ProgramState.MENU)

    def test_handle_program_state_change_no_change(self):
        """Test handling program state with no changes."""
        # Create an instance
        program_loop = ProgramLoop()

        # Set up controller with no state change
        self.mock_controller.next_state = None

        # Check state change
        program_loop.handle_program_state_change()

        # Verify results - no state change, no model update
        self.assertEqual(program_loop.current_state, ProgramState.MENU)
        self.mock_controller.update_state.assert_not_called()

    def test_handle_program_state_change_to_game(self):
        """Test handling program state change to game."""
        # Create an instance
        program_loop = ProgramLoop()
        program_loop.controller = self.mock_controller

        # Set up controller with state change to game
        self.mock_controller.next_state = ProgramState.GAME
        self.mock_controller.model = Mock()
        self.mock_controller.model.settings = {"difficulty": 3}

        # Check state change
        # We need to patch where GameModel is USED, not where it's defined
        with patch('src.controllers.program_loop.GameModel') as mock_game_model:
            mock_game = Mock()
            mock_game_model.return_value = mock_game

            program_loop.handle_program_state_change()

            # Verify results
            self.assertEqual(program_loop.current_state, ProgramState.GAME)
            mock_game_model.assert_called_once_with(3)
            self.mock_controller.update_state.assert_called_once_with(mock_game)

    def test_check_and_update_settings_no_changes(self):
        """Test checking settings with no updates."""
        # Create an instance
        program_loop = ProgramLoop()
        program_loop.controller = self.mock_controller

        # Set up controller with no updates
        self.mock_controller.asset_package_updated = False
        self.mock_controller.resolution_updated = False

        # Check settings
        program_loop.check_and_update_settings()

        # Verify results
        self.mock_controller.reset_settings_update_flags.assert_called_once()

    def test_check_and_update_settings_assets(self):
        """Test checking settings with asset updates."""
        # Create an instance
        program_loop = ProgramLoop()
        program_loop.controller = self.mock_controller

        # We need to create new patches for where the functions are USED
        with patch('src.controllers.program_loop.build_asset_container') as mock_local_assets, \
                patch('src.controllers.program_loop.GameRenderer') as mock_local_renderer:
            # Create new asset container mock for this test
            new_assets_mock = Mock()
            mock_local_assets.return_value = new_assets_mock

            # Create new renderer mock for this test
            new_renderer_mock = Mock()
            mock_local_renderer.return_value = new_renderer_mock

            # Set up controller with asset updates
            self.mock_controller.asset_package_updated = True
            self.mock_controller.resolution_updated = False
            self.mock_controller.model = Mock()
            self.mock_controller.model.settings = {"theme": MenuTheme.RED}

            # Check settings
            program_loop.check_and_update_settings()

            # Verify results
            mock_local_assets.assert_called_with(MenuTheme.RED)
            mock_local_renderer.assert_called_with(new_assets_mock)
            self.mock_controller.reset_settings_update_flags.assert_called_once()

    def test_update_and_render_no_updates(self):
        """Test updating and rendering with no model updates."""
        # Create an instance
        program_loop = ProgramLoop()

        # Set up controller with no updates
        self.mock_controller.model_updated = False

        # Update and render
        program_loop.update_and_render()

        # Verify results - no rendering performed
        self.mock_controller.reset_render_flag.assert_not_called()
        self.mock_renderer.render_menu.assert_not_called()
        self.mock_renderer.render_game.assert_not_called()

    def test_update_and_render_menu_state(self):
        """Test updating and rendering in menu state."""
        # Create an instance
        program_loop = ProgramLoop()
        program_loop.controller = self.mock_controller

        # Replace the renderer with our mock directly
        program_loop.renderer = self.mock_renderer

        # Replace the controller with our mock
        program_loop.controller = self.mock_controller

        # Set up controller with updates
        self.mock_controller.model_updated = True
        program_loop.current_state = ProgramState.MENU

        # We need to patch pygame functions to avoid errors
        with patch('pygame.transform.smoothscale', return_value=MagicMock()), \
                patch('pygame.display.flip'):
            # Update and render
            program_loop.update_and_render()

        # Verify results
        self.mock_controller.reset_render_flag.assert_called_once()
        self.mock_renderer.render_menu.assert_called_once_with(
            self.mock_controller.model, self.mock_virtual_screen)
        self.mock_renderer.render_game.assert_not_called()

    def test_update_and_render_game_state(self):
        """Test updating and rendering in game state."""
        # Create an instance
        program_loop = ProgramLoop()
        program_loop.controller = self.mock_controller

        # Replace the renderer with our mock directly
        program_loop.renderer = self.mock_renderer

        # Replace the controller with our mock directly
        program_loop.controller = self.mock_controller

        # Set up controller with updates
        self.mock_controller.model_updated = True
        program_loop.current_state = ProgramState.GAME

        # We need to patch pygame functions to avoid errors
        with patch('pygame.transform.smoothscale', return_value=MagicMock()), \
                patch('pygame.display.flip'):
            # Update and render
            program_loop.update_and_render()

        # Verify results
        self.mock_controller.reset_render_flag.assert_called_once()
        self.mock_renderer.render_game.assert_called_once_with(
            self.mock_controller.model, self.mock_virtual_screen)
        self.mock_renderer.render_menu.assert_not_called()

    def test_run_program_simple(self):
        """Test a simple run of the program loop that exits after one iteration."""
        # Create an instance
        program_loop = ProgramLoop()

        # Replace the controller with our mock directly
        program_loop.controller = self.mock_controller
        self.mock_controller.model_updated = True

        # Reset the pygame.quit mock to clear previous calls
        self.mock_quit.reset_mock()

        # Mock handle_user_input to return False after first call to exit the loop
        first_call = [True]  # Using a list to create a mutable closure variable

        def mock_handle_input():
            if first_call[0]:
                first_call[0] = False
                return True  # Continue on first call
            return False  # Exit on second call

        # Set up mocks
        with patch.object(program_loop, 'handle_user_input', side_effect=mock_handle_input), \
                patch.object(program_loop, 'check_and_update_settings') as mock_check, \
                patch.object(program_loop, 'handle_program_state_change') as mock_state, \
                patch.object(program_loop, 'update_and_render') as mock_render, \
                patch('pygame.display.flip'):
            # Run the program
            program_loop.run_program()

            # Verify loop execution
            # - One initial render + two iterations in the loop
            self.assertEqual(mock_render.call_count, 3)  # Initial + two iterations
            self.assertEqual(mock_check.call_count, 2)  # Two iterations
            self.assertEqual(mock_state.call_count, 2)  # Two iterations
            self.assertEqual(self.mock_clock.tick.call_count, 2)  # Two iterations

            # Now the quit should be called exactly once in this test
            self.mock_quit.assert_called_once()

    def test_asset_loading_failure(self):
        """Test handling of asset loading failure."""
        # Temporarily modify our asset mock to return None
        original_return_value = self.mock_assets.return_value
        self.mock_assets.return_value = None

        try:
            # This should try to exit when asset_container is None
            ProgramLoop()

            # Verify exit was called with code 1
            self.mock_exit.assert_called_once_with(1)

            # Verify pygame quit was called
            self.mock_quit.assert_called_once()
        finally:
            # Restore the original return value
            self.mock_assets.return_value = original_return_value


if __name__ == '__main__':
    unittest.main()
