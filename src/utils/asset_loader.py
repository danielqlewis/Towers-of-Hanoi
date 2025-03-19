import os
import pygame
from pygame.surface import Surface


def get_asset_path(file_path: str) -> str:
    """Convert a relative asset path to an absolute path from project root"""
    # Get the src directory
    src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Go up one level to project root
    project_root = os.path.dirname(src_dir)
    # Join with assets folder and the requested file
    return os.path.join(project_root, "Assets", file_path)


def load_image(file_path: str) -> Surface:
    """Load an image using a path relative to the assets folder"""
    full_path = get_asset_path(file_path)

    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Image file not found: {full_path}")

    return pygame.image.load(full_path).convert()


def load_image_with_alpha(file_path: str) -> Surface:
    """Load an image with alpha using a path relative to the assets folder"""
    full_path = get_asset_path(file_path)

    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Image file not found: {full_path}")

    return pygame.image.load(full_path).convert_alpha()
