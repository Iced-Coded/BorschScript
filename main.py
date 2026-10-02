import sys
from borsch.runner import run_file

def main():
    if len(sys.argv) < 2:
        print("Використання: python borsch.py <файл.brsh> [--debug]")
        sys.exit(1)

    filename = sys.argv[1]
    debug_mode = "--debug" in sys.argv

    run_file(filename, show_generated_python=debug_mode)

if __name__ == "__main__":
    main()