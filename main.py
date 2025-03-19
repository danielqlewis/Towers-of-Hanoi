import sys
from src.utils.validation import verify_system_setup
from src.controllers.program_loop import ProgramLoop


def main():
    success, message = verify_system_setup()
    if not success:
        print(message)
        sys.exit(1)

    main_loop = ProgramLoop()
    main_loop.run_program()


if __name__ == "__main__":
    main()
