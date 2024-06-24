import os
from datetime import datetime
import curses
from constants import COLOR_SUCCESS, COLOR_WARNING, COLOR_ERROR
from project_menu import project_menu

def init_colors():
    curses.start_color()
    curses.init_pair(COLOR_SUCCESS, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(COLOR_WARNING, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(COLOR_ERROR, curses.COLOR_RED, curses.COLOR_BLACK)

def print_colored(x, y, stdscr, message, color):
    stdscr.addstr(x, y, message, curses.color_pair(color))
    stdscr.refresh()

def choose_projects_directory(stdscr):
    stdscr.clear()
    stdscr.addstr(2, 2, "Enter the directory to track: ", curses.A_BOLD)
    stdscr.refresh()
    curses.echo()
    directory = stdscr.getstr(2, 32).decode('utf-8')
    curses.noecho()
    return directory

def create_new_project(stdscr):
    stdscr.clear()
    stdscr.addstr(2, 2, "Enter the new project name: ", curses.A_BOLD)
    stdscr.refresh()
    curses.echo()
    pjct_name = stdscr.getstr(2, 32).decode('utf-8')
    curses.noecho()
    exit_code = os.system(f"idf.py create-project {pjct_name}")
    if exit_code != 0:
        print_colored(4, 2, stdscr, f"Error creating project. Exit code: {exit_code}", COLOR_ERROR)
    if exit_code == 0:
        os.chdir(pjct_name)
        project_menu(stdscr, pjct_name)

