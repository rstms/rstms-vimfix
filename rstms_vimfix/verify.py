# verify - verify action with single keystroke

import os
import sys

if os.name == "nt":
    import msvcrt
elif os.name == "posix":
    import termios
    import tty


def get_char():
    if os.name == "nt":
        ch = msvcrt.getch()
    elif os.name == "posix":
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    else:
        raise RuntimeError(f"unsuported OS: {os.name}")

    return ch


def verify(prompt):
    print(f"\n{prompt}? [Y/n] ", end="", flush=True)
    key = get_char()
    print()
    return key in ["\r", "\n", "y", "Y"]
