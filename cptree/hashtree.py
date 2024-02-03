"""hashtree command"""

import subprocess
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile

import click
import click.core

from .clio import CLIO
from .exception_handler import ExceptionHandler
from .hash import DEFAULT_HASH, HASHES, HashDigest
from .progress import ProgressReader
from .shell import _shell_completion
from .version import __timestamp__, __version__

header = f"{__name__.split('.')[0]} v{__version__} {__timestamp__}"


def _ehandler(ctx, option, debug):
    ctx.obj = dict(ehandler=ExceptionHandler(debug))
    ctx.obj["debug"] = debug


HASH_CHOICES = list(HASHES) + ["none"]


@click.command("hashtree", context_settings={"auto_envvar_prefix": "HASHTREE"})
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
    "-h",
    "--hash",
    type=click.Choice(HASH_CHOICES),
    default=DEFAULT_HASH,
    help="select checksum hash",
)
@click.option("-p/-P", "--progress/--no-progress", is_flag=True, help="control animated progress display")
@click.option("-a", "--ascii", is_flag=True, help="ASCII progress bar")
@click.option("-f", "--find", is_flag=True, help="use find command to auto-generate input file")
@click.option("-s/-S", "--sort/--no-sort", is_flag=True, default=True, help="sort output files")
@click.option(
    "-b",
    "--base-directory",
    type=click.Path(file_okay=False, readable=True),
    default=".",
    help="base directory for relative file list",
)
@click.argument("INFILE", type=click.Path(dir_okay=False), default="-")
@click.argument("OUTFILE", type=click.Path(dir_okay=False, writable=True), default="-")
@click.pass_context
def cli(
    ctx,
    debug,
    shell_completion,
    base_directory,
    ascii,
    find,
    hash,
    sort,
    progress,
    infile,
    outfile,
):
    """generate hash digest for list of files"""

    return hashtree(base_directory=base_directory, ascii=ascii, find=find, hash=hash, sort=sort, progress=progress, infile=infile, outfile=outfile)


def hashtree(
    base_directory,
    ascii,
    find,
    hash,
    sort,
    progress,
    infile,
    outfile,
):
    base = Path(base_directory)

    if find:
        infile = find_files(base, infile)
        if sort:
            sort_file(infile)

    hasher = HashDigest(base, hash)

    with CLIO(infile, outfile) as clio:
        with ProgressReader(clio.ifp) as reader:
            for filename in reader.readlines():
                if filename.startswith(str(base)):
                    filename = Path(filename).relative_to(base)
                digest = hasher.file_digest(filename)
                clio.ofp.write(digest + "\n")

    if sort:
        sort_file(outfile)


def sort_file(filename):

    if filename in ["-", None]:
        raise RuntimeError

    with NamedTemporaryFile(delete=False, dir=".") as ofp:
        with Path(filename).open("r") as ifp:
            subprocess.run(["sort"], stdin=ifp, stdout=ofp, check=True, text=True)
        ofp.close()
        Path(ofp.name).rename(filename)


def find_files(base, filename):

    if filename in [".", "-", None]:
        filename = NamedTemporaryFile(delete=False, dir=".").name
        click.echo(f"file list: {filename}")

    with Path(filename).open("w") as ofp:
        subprocess.run(["find", ".", "-type", "f"], cwd=str(base), stdout=ofp, check=True, text=True)

    return filename


if __name__ == "__main__":
    sys.exit(hashtree())  # pragma: no cover
