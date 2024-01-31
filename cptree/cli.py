"""Console script for cptree."""

import sys

import click
import click.core

from .cptree import cptree
from .exception_handler import ExceptionHandler
from .shell import _shell_completion
from .version import __timestamp__, __version__

header = f"{__name__.split('.')[0]} v{__version__} {__timestamp__}"


def _ehandler(ctx, option, debug):
    ctx.obj = dict(ehandler=ExceptionHandler(debug))
    ctx.obj["debug"] = debug


@click.command("cptree", context_settings={"auto_envvar_prefix": "CPTREE"})
@click.version_option(message=header)
@click.option("-d", "--debug", is_eager=True, is_flag=True, callback=_ehandler, help="debug mode")
@click.option(
    "--shell-completion",
    is_flag=False,
    flag_value="[auto]",
    callback=_shell_completion,
    help="configure shell completion",
)
@click.option(
    "--ask-create/--no-ask-create", is_flag=True, default=True, help="prompt to create missing destination directory"
)
@click.argument("SRC")
@click.argument("DST")
@click.pass_context
def cli(ctx, debug, shell_completion, src, dst, ask_create):
    """cptree top-level help"""
    return cptree(src, dst, ask_create)


if __name__ == "__main__":
    sys.exit(cli())  # pragma: no cover
