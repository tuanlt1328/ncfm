#Configuration here before build
#Date and time using datetime.strftime format. Cheat sheet can be found here: https://strftime.org/
PROGRAM_DESCRIPTION = "A lightweight, minimal file manager using ncurses and Python"
START_FROM = "path to start from"

DEFAULT_SHELL = "bash"
DEFAULT_LAUNCHER = "xdg-open"
DEFAULT_PROMPT = "ncfm 0.1.2"
ELEVATED_PROMPT = "Acting as a superuser, be careful!"
DEFAULT_DATETIME = "%d %b, %Y %H:%M:%S %Z"
DEFAULT_ELEVATOR = "sudo"
PAUSE_COMMAND = "read -n 1 -s -r"
TRASH_DATA = "~/.local/share/Trash/files"
TRASH_INFO = "~/.local/share/Trash/info"

#Keys
#Keys are case-sensitive (uppercase C means SHIFT+C) and could be affected by Caps Lock
QUIT = {"q"}
COPY = {"c"}
CUT = {"C"}
HIDDEN = {"h"}
PASTE = {"v"}
DOWN = {"KEY_DOWN"}
UP = {"KEY_UP"}
IN = {"\n", "KEY_RIGHT"}
OUT = {"KEY_LEFT"}
HELP = {"?", "KEY_F(1)"}
DELETE = {"KEY_DC"}
CONSOLE = {"b"}
NEW_FOLDER = {"n"}
ELEVATE_PRIVILEGES = {"a"}

#Representation of the keys
cosmetic = {
    "KEY_DOWN": "↓",
    "KEY_UP": "↑",
    "KEY_LEFT": "←",
    "KEY_RIGHT": "→",
    "KEY_IC": "Insert",
    "KEY_DC": "Delete",
    "\n": "Enter",
    "KEY_F(1)": "F1",
    "KEY_F(2)": "F2",
    "KEY_F(3)": "F3",
    "KEY_F(4)": "F4",
    "KEY_F(5)": "F5",
    "KEY_F(6)": "F6",
    "KEY_F(7)": "F7",
    "KEY_F(8)": "F8",
    "KEY_F(9)": "F9",
    "KEY_F(10)": "F10",
    "KEY_F(11)": "F11",
    "KEY_F(12)": "F12",
}

#Description of the keys
description = {
    "Toggle this help": HELP,
    "Copy selected item": COPY,
    "Cut selected item": CUT,
    "Paste": PASTE,
    "New folder": NEW_FOLDER,
    "Delete selected item": DELETE,
    "Toggle hidden entries": HIDDEN,
    "Move cursor up": UP,
    "Move cursor down": DOWN,
    "Open selected item": IN,
    "Move to parent": OUT,
    "Launch console": CONSOLE,
    "Act as administrator": ELEVATE_PRIVILEGES,
    "Quit ncfm": QUIT,
}

#Help message generator
def helpmsg():
    res = []
    for key in description:
        active = set()
        for k in description[key]:
            if len(k) == 1:
                if ord(k) >= 65 and ord(k) <= 90:
                    k = "Shift+"+k.lower()
            if k in cosmetic:
                k = k.replace(k, cosmetic[k])
            active.add(k)
        res.append(f"{key}: {', '.join(active)}")
    return res

if __name__ == "__main__":
    print("This script is not designed to run directly.")