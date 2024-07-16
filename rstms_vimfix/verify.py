# verify - verify action with single keystroke

import os
import sys

if os.name == "nt":
    import msvcrt
elif os.name == "posix":
    import termios
    import tty


def get_char():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def verify(prompt):
    print(f"\n{prompt}? [Y/n] ", end="", flush=True)
    if os.name == "nt":
        key = msvcrt.getch().decode()
    elif os.name == "posix":
        key = get_char()
    else:
        raise RuntimeError(f"unsuported OS: {os.name}")

    print()
    return key in ["\r", "\n", "y", "Y"]
