#!/usr/bin/env python3
import re
import shlex
import sys
import termios
import tty
from pathlib import Path
from subprocess import PIPE, run

import click


def get_char():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def strip_ansi_codes(s):
    return strip_crlf(re.sub(r"\x1B[@-_][0-?]*[ -/]*[@-~]", "", s))


def strip_crlf(s):
    return s.strip()


def eformat(error, detail):
    _, _, detail = detail.partition("--> ")
    return f"{detail}{error}"


def forge_errors(lines):
    """return quickfix error list"""
    errors = None
    for i, line in enumerate(lines):
        if errors is not None and (line.startswith("Error") or line.startswith("Warning")):
            errors.append(eformat(line, lines[i + 1]))
        if "Compiler run failed" in line:
            errors = []
    if errors is None:
        errors = []
    return errors


def flake8_errors(lines):
    raise RuntimeError("flake8 not implemented")


def black_errors(lines):
    raise RuntimeError("black not implemented")


def try_quickfix(errors):
    print("\nfix? [Y/n] ", end="", flush=True)
    key = get_char()
    print()
    if key in ["\r", "\n", "y", "Y"]:
        quickfix = Path(".quickfix")
        quickfix.write_text("\n".join(errors))
        run(["vim", "-q", str(quickfix)])
        quickfix.unlink()
    sys.exit(-1)


formats = dict(forge=forge_errors, flake8=flake8_errors, black=black_errors)


def vimfix(command, quiet, ignore_stderr, ignore_stdout, strip, fmt, output):
    """run a command, check for compile errors, and optionally run vim quickfix"""

    proc = run(shlex.split(command), stdout=PIPE, stderr=PIPE)

    if proc.returncode != 0:
        quiet = False

    if not quiet:
        sys.stdout.write(proc.stdout.decode())
        sys.stdout.flush()

    sys.stderr.write(proc.stderr.decode())
    sys.stderr.flush()

    if strip:
        stripper = strip_ansi_codes
    else:
        stripper = strip_crlf

    errors = []
    if not ignore_stdout:
        errors.extend(formats[fmt]([stripper(line) for line in proc.stdout.decode().split("\n")]))
    if not ignore_stderr:
        errors.extend(formats[fmt]([stripper(line) for line in proc.stderr.decode().split("\n")]))

    if errors:
        try_quickfix(errors)

    if output is not None and proc.returncode == 0:
        # write output file only if no errors
        with output.open("wb") as ofp:
            ofp.write(proc.stdout)

    sys.exit(proc.returncode)
