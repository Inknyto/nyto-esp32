from datetime import datetime
import curses
import os
def project_menu(stdscr, pjct):
    #todo: forbid building with sudo idf.py flash
    # it changes the build files ownership to r00t
    commands = {
        "idf.py": {
            "b": "idf.py build",
            "f": "sudo idf.py flash",
            "e": "nvim main/*.c CMakeLists.txt",
            "z": "fzf -m | xargs nvim",
        },
        "flash_command.sh": {
            "b": "echo no build scripts",
            "f": "sudo ./flash_command.sh",
            "e": "nvim *.sh",
            "z": "fzf -m | xargs nvim",
        },
    }

    while True:
        stdscr.clear()
        stdscr.refresh()
        stdscr.addstr(1, 2, f"Nyto Esp32 Flasher -  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", curses.A_BOLD)
        stdscr.addstr(3, 2, "[b]uild [f]lash [s]creen [e]dit fu[z]z [d]elete [q]uit: ", curses.A_BOLD)
        stdscr.addstr(4, 2, f"Project: {pjct} ", curses.A_BOLD)
        stdscr.addstr(6, 2, f" ".join(os.listdir()), curses.A_BOLD)
        
        command = chr(stdscr.getch())
        if command == 'q':
            os.chdir("../")
            return
        elif command == 's':
            curses.endwin()
            exit_code = os.system("sudo screen /dev/ttyUSB0 115200")
            if exit_code != 0:
                print(f"Error starting screen session. Exit code: {exit_code}")

            curses.doupdate()
        elif command == "d":
            stdscr.clear()
            stdscr.refresh()
            stdscr.addstr(4, 2, f"Delete project {pjct} ?", curses.A_BOLD)
            stdscr.addstr(6, 2, "[y]es [n]o", curses.A_BOLD)
            resp = chr(stdscr.getch())
            if resp == "y":
                os.system("rm -rf *")
                os.chdir('../')
                os.rmdir(pjct)
                return
        else:
            if command in ["b", "f", "e", "z"]:
                if os.path.isfile('CMakeLists.txt'):
                    cmd = commands['idf.py'][command]
                elif os.path.isfile('flash_command.sh'):
                    cmd = commands['flash_command.sh'][command]
                else:
                    print_colored(8, 2, stdscr, "Error: No valid build file found", COLOR_ERROR)
                    stdscr.getch()
                    continue
                
                curses.endwin()
                exit_code = os.system(cmd)
                if exit_code != 0:
                    print(f"Command failed with exit code: {exit_code}")
                else:
                    print(f"Command '{cmd}' executed successfully")
                input("Press Enter to continue...")
                curses.doupdate()
