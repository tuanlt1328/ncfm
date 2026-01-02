#!/usr/bin/env python
import curses
from curses import wrapper

def main(stdscr):
    while True:
        stdscr.refresh()
        read = stdscr.getkey()
        if read == 'q':
            break
        stdscr.clear()
        stdscr.addstr(read)
        stdscr.refresh()

wrapper(main)