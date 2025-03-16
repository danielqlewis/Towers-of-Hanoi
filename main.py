import sys
from validation import check_dependencies, check_assets
from program_loop import run_program


def main():
    if not check_dependencies():
        sys.exit(1)

    if not check_assets():
        sys.exit(1)

    run_program()


if __name__ == "__main__":
    main()
