import os
import pygame
from typing import List, Dict, Tuple, Set, Optional, Union
import logging

# Set up logging
logger = logging.getLogger(__name__)


def check_dependencies() -> bool:
    """Check that required dependencies are installed."""
    try:
        pygame.version
        return True
    except ImportError:
        logger.error("Pygame is not installed. Please install it with 'pip install pygame'.")
        return False


def get_project_root() -> str:
    """Get the absolute path to the project root directory."""
    current_dir = os.path.dirname(os.path.abspath(__file__))  # Gets the current directory
    parent_dir = os.path.dirname(current_dir)  # Go up to src
    return os.path.dirname(parent_dir)  # Go up to project root


def check_assets() -> bool:
    """Check that required game assets are present and properly organized."""
    assets_dir = os.path.join(get_project_root(), "Assets")

    # Check for main Assets folder
    if not os.path.isdir(assets_dir):
        logger.error(f"Missing main 'Assets' folder at {assets_dir}")
        return False

    # Check theme directories
    if not _check_theme_folders(assets_dir):
        return False

    # Check common images
    if not _check_common_images(assets_dir):
        return False

    return True


def _check_theme_folders(assets_dir: str) -> bool:
    """Check that theme folders exist and contain required files."""
    required_themes = ["default", "red", "blue"]

    for theme in required_themes:
        theme_path = os.path.join(assets_dir, theme)
        if not os.path.isdir(theme_path):
            logger.error(f"Missing theme folder '{theme}' in Assets directory.")
            return False

        # Check for exactly three PNG files in each theme folder
        png_files = [file for file in os.listdir(theme_path) if file.lower().endswith('.png')]
        if len(png_files) != 3:
            logger.error(f"The '{theme}' theme folder should contain exactly 3 PNG files, found {len(png_files)}.")
            return False

    return True


def _check_common_images(assets_dir: str) -> bool:
    """Check that all required common images exist in the Assets folder."""
    # Required images organized by category for better maintenance
    required_images = {
        "buttons": [
            "Accept_Button_Base.png", "Accept_Button_Selected.png",
            "Back_Button_Base.png", "Back_Button_Selected.png",
            "Credits_Button_Base.png", "Credits_Button_Selected.png",
            "Difficulty_Button_Base.png", "Difficulty_Button_Selected.png",
            "Exit_Button_Base.png", "Exit_Button_Selected.png",
            "Options_Button_Base.png", "Options_Button_Selected.png",
            "Play_Button_Base.png", "Play_Button_Selected.png",
            "Refresh_Button_Base.png", "Refresh_Button_Selected.png",
            "Resolution_Button_Base.png", "Resolution_Button_Selected.png",
            "Style_Button_Base.png", "Style_Button_Selected.png",
            "Tutorial_Button_Base.png", "Tutorial_Button_Selected.png"
        ],
        "displays": [
            "Difficulty_Display_1.png", "Difficulty_Display_2.png", "Difficulty_Display_3.png",
            "Resolution_Display_1.png", "Resolution_Display_2.png", "Resolution_Display_3.png",
            "Resolution_Display_4.png", "Resolution_Display_5.png",
            "Style_Display_1.png", "Style_Display_2.png", "Style_Display_3.png"
        ],
        "game_pieces": [
            "Plate_0_b.png", "Plate_0_s.png", "Plate_1_b.png", "Plate_1_s.png",
            "Plate_2_b.png", "Plate_2_s.png", "Plate_3_b.png", "Plate_3_s.png",
            "Plate_4_b.png", "Plate_4_s.png"
        ],
        "tutorial": [
            "Tutorial_1.png", "Tutorial_2.png", "Tutorial_3.png", "Tutorial_4.png",
            "Tutorial_5.png", "Tutorial_6.png", "Tutorial_7.png", "Tutorial_8.png",
            "Tutorial_Standin_1.png", "Tutorial_Standin_2.png", "Tutorial_Standin_3.png",
            "Tutorial_Standin_4.png", "Tutorial_Standin_5.png", "Tutorial_Standin_6.png",
            "Tutorial_Standin_7.png", "Tutorial_Standin_8.png"
        ],
        "misc": [
            "Big_X.png", "Credit_Page.png", "Victory.png"
        ]
    }

    # Flatten the dictionary into a single list
    all_required_images = []
    for category, images in required_images.items():
        all_required_images.extend(images)

    # Check each required image
    for image in all_required_images:
        if not os.path.isfile(os.path.join(assets_dir, image)):
            logger.error(f"Missing required image '{image}' in Assets folder.")
            return False

    return True


def verify_system_setup() -> Tuple[bool, str]:
    """
    Verify the complete system setup.

    Returns:
        Tuple of (success, message)
    """
    if not check_dependencies():
        return False, "Failed dependency check. See logs for details."

    if not check_assets():
        return False, "Failed assets check. See logs for details."

    return True, "System setup verified successfully."
