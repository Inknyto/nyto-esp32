import os
import sys
import curses
from main_menu import main_menu
import argparse

if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description='This project is for automating the firmware flashing on esp32 chips')
        parser.add_argument('directory', type=str, nargs='?', help='Directory of the esp32 projects using idf.py')
        args = parser.parse_args()
        directory = args.directory if args.directory else "/home/nyto/Documents/git/nyto-esp32"

        if not os.path.isdir(directory):
            print(f"Error: {directory} is not a valid directory")
            sys.exit(1)

        os.chdir(directory)
        curses.wrapper(main_menu, directory)
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
        sys.exit(0)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)

