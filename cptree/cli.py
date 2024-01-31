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


@click.command("cptree", context_settings={"auto_envvar_prefix": "CPTREE", "ignore_unknown_options": True})
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
@click.option(
    "--force-create/--no-force-create", is_flag=True, help="create missing destination directory without prompting"
)
@click.option("--progress-bar", "--no-progress-bar", is_flag=True, default=True, help="progress bar switch")
@click.argument("SRC")
@click.argument("DST")
@click.argument("RSYNC_OPTIONS", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def cli(ctx, debug, shell_completion, ask_create, force_create, progress_bar, src, dst, rsync_options):
    """rsync transfer with progress indicator and checksum verification"""
    return cptree(
        src,
        dst,
        ask_create=ask_create,
        force_create=force_create,
        rsync_options=rsync_options,
        disable=not progress_bar,
    )


if __name__ == "__main__":
    sys.exit(cli())  # pragma: no cover
