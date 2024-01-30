"""Console script for cptree."""

import sys
from pathlib import Path

import click
import click.core

from .exception_handler import ExceptionHandler
from .shell import _shell_completion
from .version import __timestamp__, __version__

header = f"{__name__.split('.')[0]} v{__version__} {__timestamp__}"


def _ehandler(ctx, option, debug):
    ctx.obj = dict(ehandler=ExceptionHandler(debug))
    ctx.obj["debug"] = debug


def verify_directory(target, src=False, dst=False):
    remote = ":" in target
    host = None
    if remote:
        raise RuntimeError("remote src/dst unimplemented")
    elif not Path(target).is_dir():
        raise RuntimeError(f"{target} is not a directory")

    return target, remote, host


@click.group("cptree", context_settings={"auto_envvar_prefix": "CPTREE"})
@click.version_option(message=header)
@click.option("-d", "--debug", is_eager=True, is_flag=True, callback=_ehandler, help="debug mode")
@click.option(
    "--shell-completion",
    is_flag=False,
    flag_value="[auto]",
    callback=_shell_completion,
    help="configure shell completion",
)
@click.argument("SRC")
@click.argument("DST")
@click.pass_context
def cli(ctx, debug, shell_completion, src, dst):
    """cptree top-level help"""
    remote_src = ":" in src
    remote_dst = ":" in dst
    src, remote_src, src_host = verify_directory(src, src=True)
    dst, remote_dst, dst_host = verify_directory(dst, dst=True)
    click.echo("rsync {src} {dst}")


if __name__ == "__main__":
    sys.exit(cli())  # pragma: no cover
