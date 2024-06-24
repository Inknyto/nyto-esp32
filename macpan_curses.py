import os
import curses
from collections import defaultdict
from packaging import version
from datetime import datetime
import click

# Color constants
COLOR_SUCCESS = 1
COLOR_WARNING = 2
COLOR_ERROR = 3

def init_colors():
    curses.start_color()
    curses.init_pair(COLOR_SUCCESS, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(COLOR_WARNING, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(COLOR_ERROR, curses.COLOR_RED, curses.COLOR_BLACK)

def print_colored(stdscr, message, color, y, x):
    stdscr.addstr(y, x, message, curses.color_pair(color))
    stdscr.refresh()

def list_packages(directory):
    package_versions = defaultdict(list)

    for package_file in os.listdir(directory):
        if package_file.endswith('.pkg.tar.xz'):
            package_name, version_str, arch = package_file.rsplit('-', 2)
            package_versions[package_name].append((version_str, arch))

    return package_versions

def show_packages_by_size(stdscr, directory):
    package_sizes = {}

    for package_file in os.listdir(directory):
        if package_file.endswith('.pkg.tar.xz'):
            try:
                file_path = os.path.join(directory, package_file)
                size_mb = os.path.getsize(file_path) / (1024 * 1024)
                package_sizes[package_file] = (size_mb, file_path)
            except OSError as e:
                print_colored(stdscr, f"Error processing {package_file}: {e}", COLOR_ERROR, 2, 2)

    if not package_sizes:
        print_colored(stdscr, "No packages found in the specified directory.", COLOR_ERROR, 2, 2)
        return

    sorted_packages = sorted(package_sizes.items(), key=lambda x: x[1][0], reverse=True)

    print_colored(stdscr, "Packages Sorted by Size (Descending):", COLOR_SUCCESS, 2, 2)
    for i, (package_file, (size_mb, file_path)) in enumerate(sorted_packages, start=3):
        package_name = package_file.split('.')[0]
        print_colored(stdscr, f"{i}. {package_name} : {size_mb:.2f} MB", COLOR_SUCCESS, i, 2)
        print_colored(stdscr, f"{file_path}", COLOR_SUCCESS, i, 22)

    stdscr.getch()

def show_package_statistics(stdscr, package_sizes):
    total_size = sum(size for size, _ in package_sizes.values())
    mean_size = total_size / len(package_sizes)
    sorted_sizes = sorted(package_sizes.values(), key=lambda x: x[0], reverse=True)
    lowest_quartile_size = sorted_sizes[len(sorted_sizes) // 4][0]
    highest_quartile_size = sorted_sizes[len(sorted_sizes) // 4 * 3][0]

    heaviest_packages = sorted(package_sizes.items(), key=lambda item: item[1][0], reverse=True)[:5]

    print_colored(stdscr, f"Total Size of the Repository: {total_size:.2f} MB", COLOR_SUCCESS, 2, 2)
    print_colored(stdscr, "5 Heaviest Packages:", COLOR_SUCCESS, 3, 2)
    for i, (package_name, (package_size, _)) in enumerate(heaviest_packages, start=4):
        print_colored(stdscr, f"{i}. {package_name}: {package_size:.2f} MB", COLOR_SUCCESS, i, 2)
    
    print_colored(stdscr, f"Mean Package Size: {mean_size:.2f} MB", COLOR_SUCCESS, i + 2, 2)
    print_colored(stdscr, f"Lowest Quartile Package Size: {lowest_quartile_size:.2f} MB", COLOR_SUCCESS, i + 3, 2)
    print_colored(stdscr, f"Highest Quartile Package Size: {highest_quartile_size:.2f} MB", COLOR_SUCCESS, i + 4, 2)

    stdscr.getch()

def choose_tracking_directory(stdscr):
    stdscr.clear()
    stdscr.addstr(2, 2, "Enter the directory to track: ", curses.A_BOLD)
    stdscr.refresh()
    curses.echo()
    directory = stdscr.getstr(2, 32).decode('utf-8')
    curses.noecho()
    return directory

def drop_outdated_packages(stdscr, package_versions, directory):
    outdated = []
    for package_name, versions in package_versions.items():
        sorted_versions = sorted(versions, key=lambda x: version.parse(x[0]), reverse=True)
        if len(sorted_versions) > 1:
            outdated.extend([(package_name, v, a) for v, a in sorted_versions[1:]])

    if outdated:
        print_colored(stdscr, "Outdated Packages to Drop:", COLOR_WARNING, 2, 2)
        for i, (pkg, ver, arch) in enumerate(outdated, start=3):
            print_colored(stdscr, f"{i}. {pkg}-{ver}-{arch}", COLOR_WARNING, i, 2)

        stdscr.addstr(i + 2, 2, "Do you want to drop the outdated packages? (y/n): ", curses.A_BOLD)
        stdscr.refresh()
        confirm_drop = stdscr.getch()
        if confirm_drop in [ord('y'), ord('Y')]:
            for pkg, ver, arch in outdated:
                file_to_drop = os.path.join(directory, f"{pkg}-{ver}-{arch}.pkg.tar.xz")
                os.remove(file_to_drop)
            print_colored(stdscr, "Outdated packages dropped.", COLOR_SUCCESS, i + 4, 2)
        else:
            print_colored(stdscr, "Operation canceled.", COLOR_SUCCESS, i + 4, 2)
    else:
        print_colored(stdscr, "No outdated packages found.", COLOR_ERROR, 2, 2)
    stdscr.getch()

def search_packages(stdscr, package_versions):
    stdscr.clear()
    stdscr.addstr(2, 2, "Enter search term: ", curses.A_BOLD)
    stdscr.refresh()
    curses.echo()
    search_term = stdscr.getstr(2, 22).decode('utf-8')
    curses.noecho()

    stdscr.clear()
    stdscr.refresh()

    print_colored(stdscr, f"Search Results for '{search_term}':", COLOR_SUCCESS, 2, 2)
    i = 3
    for package_name, versions in package_versions.items():
        if search_term.lower() in package_name.lower():
            print_colored(stdscr, f"{i}. {package_name}:", COLOR_SUCCESS, i, 2)
            i += 1
            for version_str, arch in sorted(versions, key=lambda x: version.parse(x[0]), reverse=True):
                print_colored(stdscr, f"  {version_str}-{arch}", COLOR_SUCCESS, i, 2)
                i += 1

    stdscr.getch()

def list_packages_by_location_and_time(stdscr, directory):
    packages_by_location_and_time = defaultdict(list)

    for package_file in os.listdir(directory):
        if package_file.endswith('.pkg.tar.xz'):
            file_path = os.path.join(directory, package_file)
            location, _, timestamp = package_file.rsplit('-', 2)
            packages_by_location_and_time[location].append((timestamp, file_path))

    print_colored(stdscr, "Packages by Location and Time:", COLOR_SUCCESS, 2, 2)
    i = 3
    for location, packages in packages_by_location_and_time.items():
        print_colored(stdscr, f"Location: {location}", COLOR_SUCCESS, i, 2)
        i += 1
        for timestamp, file_path in sorted(packages, key=lambda x: x[0], reverse=True):
            print_colored(stdscr, f"  Time: {timestamp}", COLOR_SUCCESS, i, 2)
            print_colored(stdscr, f"  Path: {file_path}", COLOR_SUCCESS, i + 1, 2)
            i += 2

    stdscr.getch()

def main_menu(stdscr, directory, package_versions):
    init_colors()
    curses.curs_set(0)
    stdscr.clear()

    while True:
        stdscr.clear()
        stdscr.refresh()

        stdscr.addstr(1, 2, f"MacPan Package Manager Daemon  -  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", curses.A_BOLD)

        stdscr.addstr(3, 2, "By Inknyto", curses.A_BOLD)
        stdscr.addstr(4, 2, "Repository:", curses.A_BOLD)

        stdscr.addstr(6, 2, "1. List Packages", curses.A_BOLD)
        stdscr.addstr(7, 2, "2. Drop Outdated Packages", curses.A_BOLD)
        stdscr.addstr(8, 2, "3. Show Package Counts", curses.A_BOLD)
        stdscr.addstr(9, 2, "4. Search Packages", curses.A_BOLD)
        stdscr.addstr(10, 2, "5. Show Package Sizes", curses.A_BOLD)
        stdscr.addstr(11, 2, "6. List Packages by Location and Time", curses.A_BOLD)
        stdscr.addstr(12, 2, "7. Choose Tracking Directory", curses.A_BOLD)
        stdscr.addstr(13, 2, "0. Exit", curses.A_BOLD)

        choice = stdscr.getch()
        print(choice)

        if choice == ord('0'):
            break
        elif choice == ord('1'):
            package_versions = list_packages(directory)
            
            #list_packages_by_location_and_time(stdscr, package_versions)
        elif choice == ord('2'):
            drop_outdated_packages(stdscr, package_versions, directory)
        elif choice == ord('3'):
            total_packages = sum(len(versions) for versions in package_versions.values())
            print_colored(stdscr, f"Total Packages: {total_packages}", COLOR_SUCCESS, 15, 2)
            stdscr.getch()
        elif choice == ord('4'):
            search_packages(stdscr, package_versions)
        elif choice == ord('5'):
            show_packages_by_size(stdscr, directory)
        elif choice == ord('6'):
            list_packages_by_location_and_time(stdscr, directory)
        elif choice == ord('7'):
            directory = choose_tracking_directory(stdscr)

if __name__ == "__main__":
    directory = "pacman-packages"
    package_versions = list_packages(directory)
    curses.wrapper(main_menu, directory, package_versions)


