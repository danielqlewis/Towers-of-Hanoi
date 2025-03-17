import os
import pygame


def check_dependencies():
    """Check that required dependencies are installed."""
    try:
        pygame.version
    except ImportError:
        print("Error: Pygame is not installed. Please install it with 'pip install pygame'.")
        return False
    return True


def check_assets():
    """Check that required game assets are present and properly organized."""
    # Get the path to the assets folder relative to this script
    current_dir = os.path.dirname(os.path.abspath(__file__))  # Gets the current directory
    parent_dir = os.path.dirname(current_dir)  # Go up one level
    project_root = os.path.dirname(parent_dir)  # Go up another level
    assets_dir = os.path.join(project_root, "Assets")  # Find Assets folder

    # Check for main Assets folder
    if not os.path.isdir(assets_dir):
        print(f"Error: Missing main 'assets' folder at {assets_dir}")
        return False

    # Check for theme subfolders
    required_themes = ["default", "red", "blue"]
    for theme in required_themes:
        theme_path = os.path.join(assets_dir, theme)
        if not os.path.isdir(theme_path):
            print(f"Error: Missing theme folder '{theme}' in Assets directory.")
            return False

        # Check for exactly three PNG files in each theme folder
        png_files = [file for file in os.listdir(theme_path) if file.lower().endswith('.png')]
        if len(png_files) != 3:
            print(f"Error: The '{theme}' theme folder should contain exactly 3 PNG files, found {len(png_files)}.")
            return False

    # Check for required common images in the main Assets folder
    common_images = [
        "Accept_Button_Base.png",  # very long list omitted here
    ]

    for image in common_images:
        if not os.path.isfile(os.path.join(assets_dir, image)):
            print(f"Error: Missing required image '{image}' in Assets folder.")
            return False

    return True
