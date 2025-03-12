import os
import sys
import pygame

from program_loop import run_program


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
    # Check for main Assets folder
    if not os.path.isdir("Assets"):
        print("Error: Missing main 'Assets' folder.")
        return False

    # Check for theme subfolders
    required_themes = ["default", "red", "blue"]
    for theme in required_themes:
        theme_path = os.path.join("Assets", theme)
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
        # Add your required image filenames here, for example:
        # "background.png", "title.png", etc.
    ]

    for image in common_images:
        if not os.path.isfile(os.path.join("Assets", image)):
            print(f"Error: Missing required image '{image}' in Assets folder.")
            return False

    return True


def main():
    """Entry point for the Tower of Hanoi game."""
    print("Starting Tower of Hanoi...")

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Check assets
    if not check_assets():
        sys.exit(1)

    # Run the game
    run_program()


if __name__ == "__main__":
    main()
