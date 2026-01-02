# ncfm - ncurses file manager
## About
ncfm is a lightweight, minimal file manager using ncurses and Python ([curses](https://docs.python.org/3/library/curses.html) module).
> [!IMPORTANT]
> ncfm is in an early development state
>
## Availability
At the moment, ncfm only supports Linux. Other system requires source code modification since ncfm was developed for Linux and currently relies heavily on Linux programs and filesystems to function properly.
## Build instruction
### Requirements
- Python 3 (>= 3.15 recommended)
- ncurses (dependency of `curses` module)
- pyinstaller (to build binary application)
### Configuration
Configuration are done in [ncfm_config.py](./src/ncfm_config.py) before build. 
### Building
Run the following command: 
```bash
pyinstaller ncfm.spec
```
The executable will be available in [dist](./dist)
Copy the executable to `$PATH` and it should be available in the shell.
## License
ncfm is licensed under GNU General Public License (read [LICENSE](./LICENSE) for details).