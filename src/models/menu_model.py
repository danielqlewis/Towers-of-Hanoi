from src.constants import MenuState, MenuTheme, ButtonFlag
from src.models.button_entity import ButtonEntity


class MenuModel:
    """
    Manages menu system state and user-configurable settings.

    This class handles the current menu state (main menu, options, tutorial, credits),
    stores user settings (theme, resolution, difficulty), and tracks button states
    for menu navigation.

    Attributes:
        main_menu_buttons: List of ButtonFlag enums for the main menu.
        option_menu_buttons: List of ButtonFlag enums for the options menu.
        settings: Dictionary of current user settings (theme, resolution, difficulty).
        current_menu: Current menu state enum value.
        active_buttons: List of ButtonEntity objects for the current menu.
        highlighted_button: Currently highlighted button or None.
        settings_select_display: Temporary settings being previewed in options menu.
        tutorial_slide: Current tutorial slide index.
        total_tutorial_slides: Total number of available tutorial slides.
    """
    main_menu_buttons = [ButtonFlag.PLAY, ButtonFlag.OPTIONS, ButtonFlag.EXIT, ButtonFlag.TUTORIAL, ButtonFlag.CREDITS]
    option_menu_buttons = [ButtonFlag.DIFFICULTY_TOGGLE, ButtonFlag.RESOLUTION_TOGGLE, ButtonFlag.THEME_TOGGLE,
                           ButtonFlag.ACCEPT_SETTINGS, ButtonFlag.BACK_TO_MAIN]

    def __init__(self):
        """
        Initialize a new menu model with default settings.

        Creates a menu model with standard theme, 960x640 resolution, and
        difficulty level of 3 discs. Sets the initial state to the main menu.
        """
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
        """
        Change the current menu state and update active buttons accordingly.

        Args:
            new_state: MenuState enum value representing the desired menu state.
        """
        self.current_menu = new_state
        if self.current_menu == MenuState.MAIN:
            button_list = self.main_menu_buttons
        elif self.current_menu == MenuState.OPTIONS:
            button_list = self.option_menu_buttons
        else:
            button_list = []
        self.active_buttons = ButtonEntity.create_buttons(button_list)

    def set_highlight(self, new_highlight: ButtonFlag) -> None:
        """
        Highlight a specific button in the current menu.

        Args:
            new_highlight: ButtonFlag enum value identifying the button to highlight.
        """
        self.highlighted_button = ButtonEntity(new_highlight)

    def clear_highlight(self) -> None:
        """
        Clear any button highlighting in the current menu.
        """
        self.highlighted_button = None

    def tutorial_step(self) -> bool:
        """
        Advance to the next tutorial slide.

        Increments the current tutorial slide index and wraps back to 0
        when all slides have been shown.

        Returns:
            True if we've reached the end of the tutorial sequence, False otherwise.
        """
        self.tutorial_slide += 1
        if self.tutorial_slide == self.total_tutorial_slides:
            self.tutorial_slide = 0
            return True
        else:
            return False

    def cycle_theme_displayed(self) -> None:
        """
        Cycle through available visual themes in the options display.

        Updates the temporary settings display with the next available theme
        without changing the actual settings until they are implemented.
        """
        current_theme = self.settings_select_display[0]
        next_value = (current_theme.value + 1) % len(MenuTheme)
        self.settings_select_display[0] = MenuTheme(next_value)

    def cycle_resolution_displayed(self) -> None:
        """
        Cycle through available screen resolutions in the options display.

        Updates the temporary settings display with the next available resolution
        without changing the actual settings until they are implemented.
        """
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
        """
        Cycle through available difficulty levels in the options display.

        Updates the temporary settings display with the next available difficulty
        (number of discs) without changing the actual settings until they are implemented.
        """
        difficulties = [3, 4, 5]
        current_idx = difficulties.index(self.settings_select_display[2])
        next_idx = (current_idx + 1) % len(difficulties)
        self.settings_select_display[2] = difficulties[next_idx]

    def reset_displayed_settings(self) -> None:
        """
        Reset the displayed settings to match the current actual settings.

        Typically called when entering the options menu.
        """
        self.settings_select_display[0] = self.settings["theme"]
        self.settings_select_display[1] = self.settings["resolution"]
        self.settings_select_display[2] = self.settings["difficulty"]

    def implement_displayed_settings(self) -> None:
        """
        Apply the displayed settings to become the actual settings.

        Typically called when the user accepts changes in the options menu.
        """
        self.settings["theme"] = self.settings_select_display[0]
        self.settings["resolution"] = self.settings_select_display[1]
        self.settings["difficulty"] = self.settings_select_display[2]
