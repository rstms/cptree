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

from .checksum import compare_checksums, dst_checksum, src_checksum
from .common import parse_int
from .exceptions import ChecksumCompareFailed, RsyncTransferFailed
from .verify import verify_dst_directory, verify_output_directory, verify_src_directory
from .watcher import LineWatcher


def mkopts(kwargs):
    opts = " "
    for k, v in kwargs:
        if v:
            opts.append(f"{k} {v} ")
        else:
            opts.append(f"{k} ")
    opts = opts.strip()
    return opts


def prescan(src, dst, opts):
    click.echo("Scanning...\r", nl=False)
    scanproc = run(f"rsync -a --list-only {opts} {src} {dst}", hide=True, warn=True)
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
        "c": "char_devs",
        "b": "block_devs",
    }

    pattern = re.compile(r"^(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s(.*)$")
    size = 0
    files = []
    for item in items:
        fields = pattern.match(item).groups()
        length = parse_int(fields[1])
        size += int(length)
        file_type = item[0]
        counts[file_type] += 1
        if file_type == "-":
            files.append(fields[4])

    details = []
    for k, v in counts.items():
        if v:
            details.append(f"{names[k]}={v}")

    click.echo(f"Transferring {len(items)} items: [{', '.join(details)}]")

    if (counts["b"] + counts["c"]) > 0:
        click.confirm(
            "Attempting transfer of device nodes.  Are you certain you know what you're doing?",
            abort=True,
        )

    return size, len(items), files


def cptree(*args, output_dir=None, **kwargs):
    """call _cptree with work_dir from argument or a temp dir"""

    if output_dir:
        kwargs["output_dir"] = Path(output_dir)
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
    words = shlex.split(cmd)
    words.remove("-ii")
    ipos = words.index("--info")
    words.pop(ipos)
    words.pop(ipos)
    fpos = words.index("--out-format")
    words.pop(fpos)
    words.pop(fpos)
    return " ".join(words)


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
):
    _verify_dirs(src, dst, output_dir, create, delete)

    if rsync_args is None:
        rsync_args = ""

    bytes, items, files = prescan(src, dst, rsync_args)

    file_list = output_dir / "file_list"
    file_list.write_text("\n".join(["./" + f for f in files]) + "\n")

    ascii = bool(progress == "ascii")
    width = shutil.get_terminal_size().columns - 1

    bar = tqdm(
        total=bytes,
        unit="B",
        unit_scale=True,
        miniters=1,
        ncols=width,
        delay=1,
        ascii=ascii,
        disable=bool(progress in ["disable", False, None]),
    )

    def line_callback(line):
        click.echo(line)

    def file_callback(filename, count, length, codes):
        bar.set_description(f"[{count}/{items}]", refresh=False)

    def progress_callback(chunk, progress):
        bar.update(chunk)

    if progress:
        progress_opts = "-ii --info PROGRESS2 --out-format '~%i %l %f'"
        watcher = LineWatcher(file_callback, progress_callback, None)
    else:
        progress_opts = ""
        watcher = LineWatcher(None, None, line_callback)

    if rsync:
        cmd = f"rsync -avz {progress_opts} {rsync_args} {src} {dst}"

        # echo the rsync command without progress data output options
        click.echo(_rsync_echo(cmd))

        proc = run(
            cmd,
            watchers=[watcher],
            in_stream=None,
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

    if hash:
        _verify_hashes(src, dst, hash, output_dir, ascii, width, len(files))

    if proc is None:
        return 0
    else:
        return proc.return_code


def _verify_hashes(src, dst, hash, output_dir, ascii, width, count):
    src_sums = src_checksum(src, dst, hash, output_dir / f"src.{hash}", ascii, width, count)
    dst_sums = dst_checksum(src, dst, hash, output_dir / f"dst.{hash}", ascii, width, count)
    compare_checksums(src_sums, dst_sums)
    with src_sums.open("r") as sfp:
        ssums = len(sfp.readlines())
    with dst_sums.open("r") as dfp:
        dsums = len(dfp.readlines())
    if ssums == dsums:
        click.echo(f"\nSuccessful Transfer. Verified matching {hash.upper()} hashes on {ssums} files.\n")
    else:
        raise ChecksumCompareFailed(f"checksum count mismatch: src={ssums} dst={dsums}")
