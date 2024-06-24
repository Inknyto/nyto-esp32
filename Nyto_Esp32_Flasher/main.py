import os
import sys
import curses
from main_menu import main_menu

if __name__ == "__main__":
    try:
        directory = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else "/home/nyto/Documents/git/nyto-esp32"
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
