#!/usr/bin/env python3
import os
import re
import shlex
import sys
from pathlib import Path
from subprocess import PIPE, run

from .verify import verify


def strip_ansi_codes(s):
    return strip_crlf(re.sub(r"\x1B[@-_][0-?]*[ -/]*[@-~]", "", s))


def strip_crlf(s):
    return s.strip()


def eformat(error, detail):
    _, _, detail = detail.partition("--> ")
    return f"{detail}{error}"


def ospath(path):
    parts = Path(path).parts
    path = os.path.join(*parts)
    return path


def fix_path(line):
    path, _, tail = line.partition(":")
    return str(ospath(path)) + ":" + tail


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
    return [line for line in errors if line]


def generic_errors(lines):
    def is_error(line):
        if line.startswith("#"):
            return False
        elif ":" in line:
            return True
        else:
            return False

    return [line for line in lines if line and is_error(line)]


def black_errors(lines):
    p = re.compile(r"^error: cannot format\s(.*)")
    errors = []
    for line in lines:
        m = p.match(line)
        if m:
            line = m.groups()[0]
            file, error, row, col, source = [f.strip() for f in line.split(":")[:5]]
            line = f"{file}:{row}:{col}: [black]{error} {source}"
            errors.append(line)

    return [line for line in errors if line]


def try_quickfix(errors, localize):
    if verify("fix"):
        quickfix = Path(".quickfix")
        if localize:
            errors = [fix_path(line) for line in errors if line]
        quickfix.write_text("\n".join(errors))
        run(["vim", "-n", "-q", str(quickfix)])
        quickfix.unlink()
    sys.exit(-1)


formats = dict(forge=forge_errors, black=black_errors)


def get_formatter(command, fmt):
    if fmt is None:
        cmd = shlex.split(command)[0]
        for key in formats:
            if key == cmd:
                fmt = key
                break

    formatter = formats.get(fmt, generic_errors)
    return formatter


def vimfix(command, quiet, ignore_stderr, ignore_stdout, strip, fmt, output, localize):
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

    formatter = get_formatter(command, fmt)

    errors = []
    if not ignore_stdout:
        errors.extend(formatter([stripper(line) for line in proc.stdout.decode().split("\n")]))
    if not ignore_stderr:
        errors.extend(formatter([stripper(line) for line in proc.stderr.decode().split("\n")]))

    if len(errors):
        try_quickfix(errors, localize)

    if output is not None and proc.returncode == 0:
        # write output file only if no errors
        with output.open("wb") as ofp:
            ofp.write(proc.stdout)

    sys.exit(proc.returncode)
