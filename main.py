import sys
from src.utils.validation import check_dependencies, check_assets
from src.controllers.program_loop import ProgramLoop


def main():
    if not check_dependencies():
        sys.exit(1)

    if not check_assets():
        sys.exit(1)

    main_loop = ProgramLoop()
    main_loop.run_program()


if __name__ == "__main__":
    main()
