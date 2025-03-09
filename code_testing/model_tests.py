from models.game_model import GameModel
from models.menu_model import MenuModel
from constants import MenuState, MenuTheme, ButtonFlag


# GameModel testing ####################################################################################################

def test_game_model_initialization():
    test_model = GameModel()

    assert (test_model.towers[0] == [2, 1, 0])
    assert (test_model.towers[1] == [])
    assert (test_model.towers[2] == [])
    print("Success")


def test_game_model_move_disc():
    test_model = GameModel()

    test_model.move_disc(0, 1)
    assert test_model.towers[0] == [2, 1]
    assert test_model.towers[1] == [0]
    test_model.move_disc(0, 2)
    test_model.move_disc(1, 2)
    assert test_model.towers[0] == [2]
    assert test_model.towers[1] == []
    assert test_model.towers[2] == [1, 0]


def test_game_model_move_validation():
    test_model = GameModel()

    check1 = test_model.check_move_legal(1, 0)
    assert (check1 is False)
    check2 = test_model.check_move_legal(0, 1)
    assert (check2 is True)
    test_model.move_disc(0, 1)
    check3 = test_model.check_move_legal(0, 1)
    assert (check3 is False)
    check4 = test_model.check_move_legal(1, 0)
    assert (check4 is True)


def test_game_model_win_condition():
    test_model = GameModel()

    test_model.towers = ([], [], [2, 1, 0])
    assert test_model.is_complete() is True


def test_game_model_reset():
    test_model = GameModel()

    test_model.move_disc(0, 1)
    test_model.move_disc(0, 2)
    test_model.move_disc(1, 2)
    test_model.move_disc(0, 1)
    assert test_model.towers[0] != [2, 1, 0]
    test_model.reset_board()
    assert test_model.towers[0] == [2, 1, 0]
    assert test_model.towers[1] == []
    assert test_model.towers[2] == []


# MenuModel testing ####################################################################################################


def test_menu_model_initialization():
    test_model = MenuModel()

    assert test_model.current_menu == MenuState.MAIN
    assert test_model.settings["theme"] == MenuTheme.STANDARD
    assert test_model.highlighed_button is None
    assert test_model.settings_select_display[1] == (960, 640)
    assert test_model.tutorial_slide == 0


def test_menu_model_navigation():
    test_model = MenuModel()

    test_model.update_menu_state(MenuState.OPTIONS)
    assert test_model.current_menu == MenuState.OPTIONS
    test_model.update_menu_state(MenuState.TUTORIAL)
    assert test_model.current_menu == MenuState.TUTORIAL


def test_menu_model_highlight_toggle():
    test_model = MenuModel()

    test_model.set_highlight(ButtonFlag.PLAY)
    assert test_model.highlighed_button == ButtonFlag.PLAY
    test_model.deset_highlight()
    assert test_model.highlighed_button is None
    test_model.set_highlight(ButtonFlag.OPTIONS)
    assert test_model.highlighed_button == ButtonFlag.OPTIONS
    test_model.set_highlight(ButtonFlag.TUTORIAL)
    assert test_model.highlighed_button == ButtonFlag.TUTORIAL


def test_menu_model_settings_cycle():
    test_model = MenuModel()

    assert test_model.settings_select_display[0] == MenuTheme.STANDARD
    test_model.cycle_theme_displayed()
    assert test_model.settings_select_display[0] == MenuTheme.RED
    test_model.cycle_theme_displayed()
    assert test_model.settings_select_display[0] == MenuTheme.BLUE
    test_model.cycle_theme_displayed()
    assert test_model.settings_select_display[0] == MenuTheme.STANDARD

    assert test_model.settings_select_display[1] == (960, 640)
    test_model.cycle_resolution_displayed()
    assert test_model.settings_select_display[1] == (1080, 720)
    test_model.cycle_resolution_displayed()
    test_model.cycle_resolution_displayed()
    assert test_model.settings_select_display[1] == (720, 480)

    assert test_model.settings_select_display[2] == 3
    test_model.cycle_difficulty_displayed()
    test_model.cycle_difficulty_displayed()
    assert test_model.settings_select_display[2] == 5
    test_model.cycle_difficulty_displayed()
    assert test_model.settings_select_display[2] == 3


def test_menu_model_implement_settings():
    test_model = MenuModel()
    test_model.cycle_theme_displayed()
    test_model.cycle_resolution_displayed()
    test_model.cycle_resolution_displayed()
    test_model.implement_displayed_settings()
    assert test_model.settings["theme"] == MenuTheme.RED
    assert test_model.settings["resolution"] == (1296, 864)
    assert test_model.settings["difficulty"] == 3


def test_menu_model_tutorial_processing():
    test_model = MenuModel()
    assert test_model.tutorial_step() is False
    assert test_model.tutorial_step() is False
    assert test_model.tutorial_step() is False
    assert test_model.tutorial_step() is False
    assert test_model.tutorial_step() is False
    assert test_model.tutorial_step() is False
    assert test_model.tutorial_step() is True
