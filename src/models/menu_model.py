from src.constants import MenuState, MenuTheme, ButtonFlag
from src.models.button_container import ButtonContainer


class MenuModel:
    main_menu_buttons = [ButtonFlag.PLAY, ButtonFlag.OPTIONS, ButtonFlag.EXIT, ButtonFlag.TUTORIAL, ButtonFlag.CREDITS]
    option_menu_buttons = [ButtonFlag.DIFFICULTY_TOGGLE, ButtonFlag.RESOLUTION_TOGGLE, ButtonFlag.THEME_TOGGLE,
                           ButtonFlag.ACCEPT_SETTINGS, ButtonFlag.BACK_TO_MAIN]

    def __init__(self):
        self.settings = {
            "theme": MenuTheme.STANDARD,
            "resolution": (960, 640),
            "difficulty": 3  # Number of discs
        }

        self.current_menu = None
        self.active_buttons = []

        self.highlighted_button = None
        self.settings_select_display = [MenuTheme.STANDARD, (960, 640), 3]

        self.tutorial_slide = 0
        self.total_tutorial_slides = 8

        self.update_menu_state(MenuState.MAIN)


    def update_menu_state(self, new_state: MenuState) -> None:
        self.current_menu = new_state
        if self.current_menu == MenuState.MAIN:
            button_list = self.main_menu_buttons
        elif self.current_menu == MenuState.OPTIONS:
            button_list = self.option_menu_buttons
        else:
            button_list = []
        self.active_buttons = ButtonContainer.create_buttons(button_list)

    def set_highlight(self, new_highlight: ButtonFlag) -> None:
        self.highlighted_button = ButtonContainer(new_highlight)

    def clear_highlight(self) -> None:
        self.highlighted_button = None

    def tutorial_step(self) -> bool:
        self.tutorial_slide += 1
        if self.tutorial_slide == self.total_tutorial_slides:
            self.tutorial_slide = 0
            return True
        else:
            return False

    def cycle_theme_displayed(self) -> None:
        current_theme = self.settings_select_display[0]
        next_value = (current_theme.value + 1) % len(MenuTheme)
        self.settings_select_display[0] = MenuTheme(next_value)

    def cycle_resolution_displayed(self) -> None:
        resolutions = [
            (720, 480),
            (864, 576),
            (960, 640),
            (1080, 720),
            (1296, 864)
        ]
        current_idx = resolutions.index(self.settings_select_display[1])
        next_idx = (current_idx + 1) % len(resolutions)
        self.settings_select_display[1] = resolutions[next_idx]

    def cycle_difficulty_displayed(self) -> None:
        difficulties = [3, 4, 5]
        current_idx = difficulties.index(self.settings_select_display[2])
        next_idx = (current_idx + 1) % len(difficulties)
        self.settings_select_display[2] = difficulties[next_idx]

    def reset_displayed_settings(self) -> None:
        self.settings_select_display[0] = self.settings["theme"]
        self.settings_select_display[1] = self.settings["resolution"]
        self.settings_select_display[2] = self.settings["difficulty"]

    def implement_displayed_settings(self) -> None:
        self.settings["theme"] = self.settings_select_display[0]
        self.settings["resolution"] = self.settings_select_display[1]
        self.settings["difficulty"] = self.settings_select_display[2]
