"""Console script for rstms_vimfix."""

import shlex
import sys
from pathlib import Path

import click
import click.core

from .exception_handler import ExceptionHandler
from .shell import _shell_completion
from .version import __timestamp__, __version__
from .vimfix import formats, vimfix

header = f"{__name__.split('.')[0]} v{__version__} {__timestamp__}"


def _ehandler(ctx, option, debug):
    ctx.obj = dict(ehandler=ExceptionHandler(debug))
    ctx.obj["debug"] = debug


@click.command("vimfix", context_settings={"auto_envvar_prefix": "VIMFIX"})
@click.version_option(message=header)
@click.option(
    "-d",
    "--debug",
    is_eager=True,
    is_flag=True,
    callback=_ehandler,
    help="debug mode",
)
@click.option(
    "--shell-completion",
    is_flag=False,
    flag_value="[auto]",
    callback=_shell_completion,
    help="configure shell completion",
)
@click.option("-q", "--quiet", is_flag=True, help="no echo stdout")
@click.option("-E", "--ignore-stderr", is_flag=True, help="ignore stderr when scanning")
@click.option("-O", "--ignore-stdout", is_flag=True, help="ignore stdout when scanning")
@click.option("-l/-L", "--localize/--no-localize", is_flag=True, help="localize source file path in error output")
@click.option(
    "-s/-S",
    "--strip/--no-strip",
    is_flag=True,
    default=True,
    help="strip ANSI codes",
)
@click.option(
    "-f",
    "--format",
    "fmt",
    type=click.Choice(list(formats.keys())),
)
@click.option(
    "-o",
    "--output",
    type=click.Path(dir_okay=False, writable=True, path_type=Path),
)
@click.argument("command", nargs=-1)
@click.pass_context
def cli(
    ctx,
    debug,
    shell_completion,
    quiet,
    ignore_stderr,
    ignore_stdout,
    strip,
    fmt,
    output,
    localize,
    command,
):

    if len(command) == 0:
        raise click.BadArgumentUsage("missing COMMAND", ctx=ctx)
    elif len(command) == 1:
        command = command[0]
    else:
        command = shlex.join(command)

    vimfix(command, quiet, ignore_stderr, ignore_stdout, strip, fmt, output, localize)


if __name__ == "__main__":
    sys.exit(cli())  # pragma: no cover
