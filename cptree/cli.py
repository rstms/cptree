"""Console script for cptree."""

import sys

import click
import click.core
from hashtree.hash import DEFAULT_HASH, HASHES

from .cptree import cptree
from .exception_handler import ExceptionHandler
from .shell import _shell_completion
from .version import __timestamp__, __version__

header = f"{__name__.split('.')[0]} v{__version__} {__timestamp__}"


def _ehandler(ctx, option, debug):
    ctx.obj = dict(ehandler=ExceptionHandler(debug))
    ctx.obj["debug"] = debug


FLAG_CHOICES = ["ask", "force", "never"]
HASH_CHOICES = list(HASHES) + ["none"]
PROGRESS_CHOICES = ["enable", "ascii", "none"]


@click.command("cptree", context_settings={"auto_envvar_prefix": "CPTREE"})
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
@click.option(
    "-c",
    "--create",
    type=click.Choice(FLAG_CHOICES),
    default="ask",
    help="create DST if nonexistent",
)
@click.option(
    "-D",
    "--delete",
    type=click.Choice(FLAG_CHOICES + ["force-no-countdown"]),
    default="never",
    help="delete DST contents before transfer",
)
@click.option(
    "-p",
    "--progress",
    type=click.Choice(PROGRESS_CHOICES),
    default="enable",
    help="total transfer progress",
)
@click.option(
    "-o",
    "--output",
    type=click.Path(file_okay=False, writable=True),
    help="checksum output dir",
)
@click.option(
    "-h",
    "--hash",
    type=click.Choice(HASH_CHOICES),
    default=DEFAULT_HASH,
    help="select checksum hash",
)
@click.option(
    "-r/-R",
    "--rsync/--no-rsync",
    is_flag=True,
    default=True,
    help="enable/disable rsync transfer",
)
@click.option("-a", "--rsync-args", help="rsync pass-through arguments")
@click.argument("SRC")
@click.argument("DST")
@click.pass_context
def cli(
    ctx,
    debug,
    shell_completion,
    create,
    delete,
    progress,
    output,
    hash,
    rsync,
    rsync_args,
    src,
    dst,
):
    """rsync transfer with progress indicator and checksum verification"""
    if create == "never":
        create = False
    if delete == "never":
        delete = False
    if hash == "none":
        hash = None
    if progress == "none":
        progress = None

    if src[-1] != "/":
        if click.confirm(f"Change source to {src + '/'} ?", default="Y"):
            src += "/"

    return cptree(
        src,
        dst,
        create=create,
        delete=delete,
        progress=progress,
        output_dir=output,
        hash=hash,
        rsync=rsync,
        rsync_args=rsync_args,
    )


if __name__ == "__main__":
    sys.exit(cli())  # pragma: no cover
