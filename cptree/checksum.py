# generate checksum for a list of files

import atexit
import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory

import click
from invoke import run
from tqdm import tqdm

from .common import host_mode, runner, split_target, which
from .exceptions import ChecksumCompareFailed, ChecksumGenerationFailed
from .watcher import LineWatcher


def is_remote(host):
    return bool(host)


def is_local(host):
    return not bool(host)


def checksum(target, hash, output_file, tqdm_kwargs=None, src=None, dst=None):
    """generate BSD-style checksum for each file in target, returning local file containing result"""

    if tqdm_kwargs is None:
        tqdm_kwargs = dict(disable=True)

    host, base = split_target(target)
    base = Path(base.rstrip("/"))

    if is_local(host):
        base = base.resolve()

    if src:
        label = "source"
    elif dst:
        label = "destination"
    else:
        raise RuntimeError

    click.echo(f"Generating checksums for {host_mode(host)} {label} {target}")

    # try linux command without breaking
    hash_cmd = which(hash + "sum", host, quiet=True)
    if hash_cmd:
        # add option if linux
        hash_cmd += " --tag"
    else:
        # try bsd-style hash command
        hash_cmd = which(hash, host)

    with NamedTemporaryFile("w+", delete=False) as tempfile:

        with tqdm(unit=" lines", **tqdm_kwargs) as bar:

            atexit.register(delete_file, tempfile.name)

            def _line(line):
                bar.update(1)

            cmd = f"cd {str(base)}; {which('find', host)} . -type f -exec {hash_cmd} \\{{\\}} \\;"
            genproc = runner(host)(
                cmd,
                warn=True,
                watchers=[LineWatcher(line_callback=_line)],
                hide=True,
                in_stream=False,
                out_stream=tempfile.file,
            )

            if genproc.failed:
                raise ChecksumGenerationFailed(genproc.stderr)

        tempfile.close()

        # sort checksums into output file
        with output_file.open("w") as ofp:
            run(f"{which('sort')} {tempfile.name}", in_stream=False, out_stream=ofp, hide=True)

    return output_file


def delete_file(filename):
    Path(filename).unlink()


def compare_checksums(src_sums, dst_sums):
    """run diff on hash digest files, return length if identical, otherwise raise exception"""

    diff = run(f"{which('diff')} {str(src_sums)} {str(dst_sums)}", in_stream=False, hide=True, warn=True)
    if diff.failed:
        output_dir = Path(src_sums).parent
        (output_dir / "cptree.diff.out").write_text(diff.stdout)
        (output_dir / "cptree.diff.err").write_text(diff.stderr)
        tempdir = TemporaryDirectory(prefix="cptree", delete=False)
        shutil.copytree(output_dir, tempdir)
        raise ChecksumCompareFailed("details written to {tempdir.name}")
    wc = run(f"{which('wc')} -l {str(src_sums)}", in_stream=False, hide=True)
    return int(wc.stdout.split()[0])
