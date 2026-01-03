#!/usr/bin/env python
import os
from glob import glob
import argparse
import traceback
import subprocess
import shutil
import ncfm_config
from datetime import datetime, timezone
from sys import argv, exit, executable
import sys

if getattr(sys, 'frozen', False):
    os.environ.setdefault(
        "TERMINFO",
        os.path.join(sys._MEIPASS, "terminfo")
    )

import curses

stdscr = None
prompt = ncfm_config.DEFAULT_PROMPT
lastend = ""
selected = 0
window=0
WINDOW_START = 1
WINDOW_SIZE = 0
clipboard = ""
cut = False
hidden = False
entries = []

parser = argparse.ArgumentParser(description=ncfm_config.PROGRAM_DESCRIPTION)
parser.add_argument("-s", "--start", default=os.getcwd(), type=str, help=ncfm_config.START_FROM)
args = parser.parse_args()

if args.start:
    try:
        os.chdir(args.start)
    except FileNotFoundError:
        prompt = f"Path do not exist, start from '{os.getcwd()}' instead"

def init():
    global stdscr
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    curses.curs_set(0)

def quit():
    curses.curs_set(1)
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()

def readstr(y, x, prom):
    stdscr.addstr(y, x, prom)
    curses.echo()
    inp = stdscr.getstr(y, x+len(prom)).decode('utf-8')
    curses.noecho()
    return inp

def getch():
    os.system(ncfm_config.PAUSE_COMMAND)

def get_timezone():
    local_aware_dt = datetime.now(timezone.utc).astimezone()
    local_tzinfo = local_aware_dt.tzinfo
    return local_tzinfo

def priority(path):
    if path == "..":
        return -1
    prio=2
    if os.path.isdir(path):
        prio=0

    if os.path.islink(path):
        prio=1
    return prio

def askyesno(prompt: str, x:int, y:int, default:bool = False) -> bool:
    if default:
        option = "(Y/n)"
    else:
        option = "(y/N)"
    stdscr.addnstr(x, y, prompt+" "+option, curses.COLS)
    answer = stdscr.getkey()
    if answer.lower() == 'y':
        return True
    elif answer.lower() == 'n':
        return False
    else: return default

def get_entry(hidden: bool = False):
    absPaths = glob(os.path.join(os.getcwd(),"**"), include_hidden=hidden)
    possibleEntries = [os.path.split(path)[1] for path in absPaths]
    if(os.getcwd()!="/"):
        possibleEntries.append('..')
    possibleEntries.sort(key=lambda entry: (priority(entry),entry))
    return possibleEntries

def execute(function: callable, *args):
    global prompt
    try:
        function(*args)
    except PermissionError:
        prompt = "Permission denied."
    except FileNotFoundError:
        prompt = "No such file or directory."
    except FileExistsError:
        prompt = "File or directory already existed."
    except Exception as e:
        prompt = e.__str__()


def action_copy():
    global prompt, clipboard
    cont=False
    if entries[selected] == "..":
        if not askyesno("Copy '..' is not recommended. Proceed?", curses.LINES-1, 0):
            cont=True
    if cont:
        return
    prompt = f"Copy '{entries[selected]}'"
    clipboard = os.path.abspath(entries[selected])
    cut = False

def action_cut():
    global prompt, clipboard
    cont=False
    if entries[selected] == "..":
        if not askyesno("Cut '..' is not recommended. Proceed?", curses.LINES-1, 0):
            cont=True
    if cont:
        return
    prompt = f"Cut '{entries[selected]}'"
    clipboard = os.path.abspath(entries[selected])
    cut = True

def action_paste():
    global clipboard, cut, lastend
    last = os.path.split(clipboard)[1]
    if last in entries:
        prompt = f"{last} already exist, aborted."
        return
    if cut:
        execute(shutil.move, clipboard, os.path.join(os.getcwd(), last))
        clipboard = os.path.join(os.getcwd(), last)
        cut = False
    else:
        if os.path.isdir:
            execute(shutil.copytree, clipboard, os.path.join(os.getcwd(), last))
        else:
            execute(shutil.copy2, clipboard, os.path.join(os.getcwd(), last))
    lastend = last

def action_help():
    if curses.COLS < 30:
        quit()
        print(ncfm_config.helpmsg())
        getch()
        init()
    msg = ncfm_config.helpmsg()
    width = len(max(msg, key=len))+4
    height = min(len(msg)+3, curses.LINES)
    hx = (curses.COLS - width)//2
    hy = (curses.LINES - height)//2
    help_window = curses.newwin(height, width, hy, hx)
    helpcursor = 0
    helprun = True
    while helprun:
        help_window.clear()
        help_window.box()
        help_window.addstr(0, 1, "ncfm help")
        for i in range(0, height-1):
            if i+helpcursor >= len(msg):
                break
            help_window.addstr(i+2, 2, msg[i+helpcursor])
        help_window.refresh()
        helpcmd = stdscr.getkey()
        if helpcmd in ncfm_config.QUIT or helpcmd in ncfm_config.HELP:
            helprun = False

def action_delete():
    global selected
    fullPath = os.path.join(os.getcwd(), entries[selected])
    with open(os.path.join(os.path.expanduser(ncfm_config.TRASH_INFO),f"{entries[selected]}.trashinfo"), "w") as tri:
        tri.write(f"[Trash Info]\nPath={fullPath}\nDeletionDate={datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}")
    execute(shutil.move, fullPath, os.path.join(os.path.expanduser(ncfm_config.TRASH_DATA), entries[selected]))
    if selected >= len(entries):
        selected = len(entries)-1

init()

WINDOW_SIZE = curses.LINES-2

try:
    while True:
        stdscr.clear()
        curses.LINES, curses.COLS = stdscr.getmaxyx()
        entries = get_entry(hidden)

        if lastend != "" and lastend in entries:
            selected = entries.index(lastend)
            if os.path.isdir(lastend):
                if selected > window+(curses.LINES//2):
                    window = selected-(curses.LINES//2)
                    if selected+(curses.LINES//2) >= len(entries):
                        window = len(entries)-WINDOW_SIZE-1
            lastend = ""
        while selected >= window+WINDOW_SIZE:
            window+=1
        while selected < window:
            window-=1
        if prompt == ncfm_config.DEFAULT_PROMPT and os.getuid() == 0:
            prompt = ncfm_config.ELEVATED_PROMPT
        stdscr.addstr(curses.LINES-1, 0, " "*(curses.COLS-1))
        stdscr.addstr(curses.LINES-1, 0, prompt)
        prompt = ncfm_config.DEFAULT_PROMPT

        
        #Render header
        header = f" {os.getcwd()} - NCFM "
        while(len(header) < curses.COLS):
            header = "-"+header+"-"
        stdscr.addnstr(0,0, header, curses.COLS)
        
        #Render items
        for i in range(window, window+WINDOW_SIZE):
            if i >= len(entries):
                break
            tp="f"
            modified_time = datetime.fromtimestamp(os.path.getmtime(entries[i]), get_timezone())
            if os.path.isdir(entries[i]):
                tp = "d"
            if os.path.islink(entries[i]):
                tp = "l"
            line = f"{tp}  {modified_time.strftime(ncfm_config.DEFAULT_DATETIME)} \t {entries[i]}"
            if i == selected:
                stdscr.addstr(i-window+WINDOW_START,0," "*curses.COLS, curses.A_REVERSE)
                stdscr.addstr(i-window+WINDOW_START,0,line, curses.A_REVERSE)
            else:
                stdscr.addstr(i-window+WINDOW_START,0," "*curses.COLS)
                stdscr.addstr(i-window+WINDOW_START,0,line)

        stdscr.refresh()
        read = stdscr.getkey()
        
        if read in ncfm_config.QUIT:
            break

        elif read in ncfm_config.COPY:
            action_copy()

        elif read in ncfm_config.CUT:
            action_cut()

        elif read in ncfm_config.HIDDEN:
            hidden = not hidden

        elif read in ncfm_config.PASTE:
            action_paste()
            
        elif read in ncfm_config.DOWN:
            selected = (selected+1)%(len(entries))
            
        elif read in ncfm_config.UP:
            selected = (selected-1)%(len(entries))

        elif read in ncfm_config.HELP:
            action_help()
        
        elif read in ncfm_config.CONSOLE:
            quit()
            subprocess.run([ncfm_config.DEFAULT_SHELL])
            init()

        elif read in ncfm_config.IN or read in ncfm_config.OUT:
            chosen_element = entries[selected]
            lastend = os.path.split(os.getcwd())[1]
            if read in ncfm_config.OUT:
                chosen_element = ".."
            if(chosen_element!=".."):
                lastend=".."
            if(os.path.isdir(chosen_element)):
                execute(os.chdir,chosen_element)
            elif(os.path.isfile(chosen_element)):
                stdscr.move(curses.LINES-1, 0)
                stdscr.refresh()
                quit()
                subprocess.run([ncfm_config.DEFAULT_LAUNCHER, chosen_element])
                init()
                lastend = chosen_element

        elif read in ncfm_config.ELEVATE_PRIVILEGES:
            if os.getuid() == 0:
                prompt = "Already run as superuser."
                continue
            quit()
            if "python" in executable: #as script
                subprocess.run([ncfm_config.DEFAULT_ELEVATOR, executable, os.path.abspath(__file__)])
            else: #as program
                subprocess.run([ncfm_config.DEFAULT_ELEVATOR, executable])
            init()

        elif read in ncfm_config.NEW_FOLDER:
            name = readstr(curses.LINES-1, 0, "Name of the new folder: ")
            execute(os.makedirs,name)
            lastend = name

        elif read in ncfm_config.DELETE:
            action_delete()

        elif any(read in func for func in ncfm_config.description.values()):
            prompt = "Function is not implemented yet."
                

except KeyboardInterrupt:
    pass
except Exception:
    quit()
    traceback.print_exc()
    exit(0)

quit()