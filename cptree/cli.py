"""Console script for cptree."""

import sys

import click
import click.core

from .cptree import cptree
from .exception_handler import ExceptionHandler
from .shell import _shell_completion
from .version import __timestamp__, __version__

header = f"{__name__.split('.')[0]} v{__version__} {__timestamp__}"

DEFAULT_HASH = "sha256"
HASHES = ["md5", "sha1", "sha256", "sha512"]


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
    help="create destination directory if nonexistent",
)
@click.option(
    "-D",
    "--delete",
    type=click.Choice(FLAG_CHOICES + ["force-no-countdown"]),
    default="never",
    help="delete destination directory before transfer",
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
    "--output_dir",
    type=click.Path(file_okay=False, writable=True),
    help="output directory",
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
@click.option("-f", "--file-list", is_flag=True, help="scan only, output file list")
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
    output_dir,
    file_list,
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
        if file_list:
            click.echo(f"WARNING: changing source to {src + '/'}", err=True)
            src += "/"
        else:
            if click.confirm(f"Change source to {src + '/'} ?", default="Y"):
                src += "/"

    return cptree(
        src,
        dst,
        create=create,
        delete=delete,
        progress=progress,
        output_dir=output_dir,
        hash=hash,
        rsync=rsync,
        rsync_args=rsync_args,
        file_list=file_list,
    )


if __name__ == "__main__":
    sys.exit(cli())  # pragma: no cover
