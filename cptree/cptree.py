# cptree implementation

import re
import shlex
import shutil
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import click
from invoke import run
from tqdm import tqdm

from .checksum import checksum, compare_checksums
from .common import parse_int, which, write_file_lines
from .exceptions import (
    RsyncTransferFailed,
    UnrecognizedRsyncPrescanOutput,
    UnsupportedRsyncArgument,
)
from .verify import verify_dst_directory, verify_output_directory, verify_src_directory
from .watcher import LineWatcher

NAME_LENGTH = 12

RESERVED_RSYNC_ARGS = [
    "-P",
    "--progress",
    "--info",
    "-i",
    "--itemize-changes",
    "--out-format" "--debug",
    "--msgs2stderr",
    "-q",
    "--quiet",
    "-v",
    "--verbose",
]


def mkopts(kwargs):
    opts = " "
    for k, v in kwargs:
        if v:
            opts.append(f"{k} {v} ")
        else:
            opts.append(f"{k} ")
    opts = opts.strip()
    return opts


def prescan(src, dst, cmd, opts, file_list):
    if not file_list:
        click.echo("Scanning...\r", nl=False)
    scanproc = run(f"{cmd} -a --list-only {opts} {src} {dst}", in_stream=False, hide=True, warn=True)
    if scanproc.ok:
        items = scanproc.stdout.strip().split("\n")
    else:
        click.echo(scanproc.stderr, err=True)
        sys.exit(scanproc.return_code)
    counts = {
        "d": 0,
        "-": 0,
        "l": 0,
        "p": 0,
        "c": 0,
        "b": 0,
    }
    names = {
        "d": "directories",
        "-": "files",
        "l": "links",
        "p": "pipes",
        "c": "devices",
        "b": "devices",
    }

    pattern = re.compile(r"^(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s(.*)$")
    size = 0
    files = []
    for item in items:
        match = pattern.match(item)
        if not match:
            raise UnrecognizedRsyncPrescanOutput(item)
        fields = match.groups()
        file_length = parse_int(fields[1])
        size += int(file_length)
        file_type = item[0]
        counts[file_type] += 1
        if file_type == "-":
            files.append(fields[4])

    details = []
    for k, v in counts.items():
        if v:
            details.append(f"{names[k]}={v}")

    if (counts["b"] + counts["c"]) > 0:
        if file_list:
            click.output('WARNING: Transfer includes devices.', err=True) 
        else:
            click.confirm(
                "Transfer includes devices.  Are you certain you want to proceed?",
                abort=True,
            )

    if not file_list:
        click.echo(f"Transferring {len(items)} items: [{', '.join(details)}]")

    return size, items, files


def cptree(*args, output_dir=None, **kwargs):
    """call _cptree with work_dir from argument or a temp dir"""

    if output_dir:
        output_dir = Path(output_dir)
        if not output_dir.is_dir():
            output_dir.mkdir()
        kwargs["output_dir"] = output_dir
        return _cptree(*args, **kwargs)
    else:
        with TemporaryDirectory() as temp_dir:
            kwargs["output_dir"] = Path(temp_dir)
            return _cptree(*args, **kwargs)


def _verify_dirs(src, dst, output_dir, create, delete):
    verify_output_directory(output_dir)
    verify_src_directory(src)
    verify_dst_directory(dst, create, delete)


def _rsync_echo(cmd):
    """return rsync command line without our added progress formatting options"""
    hide_options = [("--info", True), ("--out-format", True), ("--progress", False)]
    words = shlex.split(cmd)
    for word, arg in hide_options:
        pos = words.index(word)
        words.pop(pos)
        if arg:
            words.pop(pos)
    click.echo(shlex.join(words))


def _check_rsync_args(args):
    """ensure progress formatting args not present in user rsync args"""
    if args is None:
        return ""
    args = shlex.split(args)
    for reserved in RESERVED_RSYNC_ARGS:
        if reserved in args:
            raise UnsupportedRsyncArgument(f"{repr(reserved)} not supported in --rsync-args")
    return shlex.join(args)


def _cptree(  # noqa: C901
    src,
    dst,
    *,
    create=None,
    delete=None,
    progress=True,
    output_dir=None,
    hash=None,
    rsync=True,
    rsync_args=None,
    file_list=False,
):
    _verify_dirs(src, dst, output_dir, create, delete)

    rsync_cmd = which("rsync")
    rsync_args = _check_rsync_args(rsync_args)

    total_bytes, items, files = prescan(src, dst, rsync_cmd, rsync_args, file_list)
    total_items = len(items)

    if file_list:
        pattern = re.compile(r'\S+\s+\S+\s+\S+\s+\S+\s+(\S+)')
        for item in items:
            match = pattern.match(item)
            filename = match.groups()[0]
            click.echo(filename)
        return 0

    file_list = write_file_lines(output_dir, "cptree.files", ["./" + f for f in files])

    tqdm_kwargs = dict(
        total=total_bytes,
        disable=bool(progress in ["disable", False, None]),
        ascii=bool(progress == "ascii"),
        ncols=shutil.get_terminal_size().columns - 1,
        miniters=1,
        delay=1,
    )

    bar = tqdm(unit="B", unit_scale=True, **tqdm_kwargs)

    def _line(line):
        click.echo(line)

    def _file(filename, item_count, length, codes):
        count = str(item_count).zfill(len(str(total_items)))
        bar.set_description(f"[{count}/{total_items}]", refresh=False)

    def _progress(bytes_read, percent):
        bar.update(bytes_read)

    if progress:
        progress_args = "--progress --info PROGRESS2 --out-format '~%i %l %f'"
        watcher = LineWatcher(file_callback=_file, progress_callback=_progress)
    else:
        progress_args = ""
        watcher = LineWatcher(line_callback=_line)

    if rsync:

        cmd = f"{rsync_cmd} -avz {rsync_args} {progress_args} {src} {dst}"
        _rsync_echo(cmd)

        proc = run(
            cmd,
            watchers=[watcher],
            in_stream=False,
            hide=True,
            warn=True,
        )
        rsync_stderr = proc.stderr.strip().split("\n")
    else:
        click.echo("Skipping rsync transfer")
        rsync_stderr = []
        proc = None

    bar.close()

    for error in rsync_stderr:
        if error.strip():
            click.echo(error, err=True)

    if proc is not None and proc.failed:
        raise RsyncTransferFailed(f"rsync failed with error code: {proc.return_code}")

    tqdm_kwargs["total"] = len(files)
    if hash:
        _verify_hashes(src, dst, hash, output_dir, tqdm_kwargs)

    if proc is None:
        return 0
    else:
        return proc.return_code


def _verify_hashes(src, dst, hash, output_dir, tqdm_kwargs):
    src_sums = checksum(src, hash, output_dir / f"cptree.src.{hash}", tqdm_kwargs, src=True)
    dst_sums = checksum(dst, hash, output_dir / f"cptree.dst.{hash}", tqdm_kwargs, dst=True)
    count = compare_checksums(src_sums, dst_sums)
    click.echo(f"\nSuccessful Transfer. Verified matching {hash.upper()} hashes on {count} files.\n")
