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
        "Accept_Button_Base.png",
        "Accept_Button_Selected.png",
        "Back_Button_Base.png",
        "Back_Button_Selected.png",
        "Big_X.png",
        "Credits_Button_Base.png",
        "Credits_Button_Selected.png",
        "Credit_Page.png",
        "Difficulty_Button_Base.png",
        "Difficulty_Button_Selected.png",
        "Difficulty_Display_1.png",
        "Difficulty_Display_2.png",
        "Difficulty_Display_3.png",
        "Exit_Button_Base.png",
        "Exit_Button_Selected.png",
        "Options_Button_Base.png",
        "Options_Button_Selected.png",
        "Plate_0_b.png",
        "Plate_0_s.png",
        "Plate_1_b.png",
        "Plate_1_s.png",
        "Plate_2_b.png",
        "Plate_2_s.png",
        "Plate_3_b.png",
        "Plate_3_s.png",
        "Plate_4_b.png",
        "Plate_4_s.png",
        "Play_Button_Base.png",
        "Play_Button_Selected.png",
        "Refresh_Button_Base.png",
        "Refresh_Button_Selected.png",
        "Resolution_Button_Base.png",
        "Resolution_Button_Selected.png",
        "Resolution_Display_1.png",
        "Resolution_Display_2.png",
        "Resolution_Display_3.png",
        "Resolution_Display_4.png",
        "Resolution_Display_5.png",
        "Style_Button_Base.png",
        "Style_Button_Selected.png",
        "Style_Display_1.png",
        "Style_Display_2.png",
        "Style_Display_3.png",
        "Tutorial_1.png",
        "Tutorial_2.png",
        "Tutorial_3.png",
        "Tutorial_4.png",
        "Tutorial_5.png",
        "Tutorial_6.png",
        "Tutorial_7.png",
        "Tutorial_8.png",
        "Tutorial_Button_Base.png",
        "Tutorial_Button_Selected.png",
        "Tutorial_Standin_1.png",
        "Tutorial_Standin_2.png",
        "Tutorial_Standin_3.png",
        "Tutorial_Standin_4.png",
        "Tutorial_Standin_5.png",
        "Tutorial_Standin_6.png",
        "Tutorial_Standin_7.png",
        "Tutorial_Standin_8.png",
        "Victory.png"
    ]

    for image in common_images:
        if not os.path.isfile(os.path.join(assets_dir, image)):
            print(f"Error: Missing required image '{image}' in Assets folder.")
            return False

    return True
