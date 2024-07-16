"""Console script for rstms_vimfix."""

import sys
from pathlib import Path

import click
import click.core

from .version import __version__, __timestamp__
from .exception_handler import ExceptionHandler
from .vimfix import vimfix, formats


from .shell import _shell_completion

header = f"{__name__.split('.')[0]} v{__version__} {__timestamp__}"


def _ehandler(ctx, option, debug):
    ctx.obj = dict(ehandler=ExceptionHandler(debug))
    ctx.obj["debug"] = debug


@click.command("vimfix", context_settings={"auto_envvar_prefix": "VIMFIX"})
@click.version_option(message=header)
@click.option("-d", "--debug", is_eager=True, is_flag=True, callback=_ehandler, help="debug mode")
@click.option("--shell-completion", is_flag=False, flag_value="[auto]", callback=_shell_completion, help="configure shell completion")
@click.option("-c", "--command", help="command to run", required=True)
@click.option("-q", "--quiet", is_flag=True, help="no echo stdout")
@click.option("-E", "--ignore-stderr", is_flag=True, help="ignore stderr when scanning")
@click.option("-O", "--ignore-stdout", is_flag=True, help="ignore stdout when scanning")
@click.option(
    "-s/-S", "--strip/--no-strip", is_flag=True, default=True, help="strip ANSI codes"
)
@click.option(
    "-f",
    "--format", "fmt",
    type=click.Choice(list(formats.keys())),
    default=list(formats.keys())[0],
)
@click.option(
    "-o", "--output", type=click.Path(dir_okay=False, writable=True, path_type=Path)
)

def cli(ctx, debug, shell_completion, command, quiet, ignore_stderr, ignore_stdout, strip, fmt, output):
    quickfix(command, quiet, ignore_stderr, ignore_stdout, strip, fmt, output)

if __name__ == "__main__":
    sys.exit(cli())  # pragma: no cover
