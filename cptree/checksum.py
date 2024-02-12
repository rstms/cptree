# generate checksum for a list of files

import atexit
import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile, mkdtemp

import click
from invoke import run
from tqdm import tqdm

from .common import host_mode, runner, split_target, which
from .exceptions import (
    ChecksumCompareFailed,
    ChecksumExcludeFileGenerationFailed,
    ChecksumGenerationFailed,
)
from .exclude import rsync_exclude_patterns
from .watcher import LineWatcher


def is_remote(host):
    return bool(host)


def is_local(host):
    return not bool(host)


def checksum(target, hash, output_file, tqdm_kwargs=None, rsync_args=None, src=None, dst=None):
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

    exclude_filename = generate_exclude_file(host, rsync_args)

    with NamedTemporaryFile("w+", delete=False) as tempfile:

        with tqdm(unit=" lines", **tqdm_kwargs) as bar:

            atexit.register(delete_file, tempfile.name)

            def _line(line):
                bar.update(1)

            cmd = checksum_command(base, host, exclude_filename, hash_cmd)
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

        if exclude_filename:
            delete_exclude_file(host, exclude_filename)

        # sort checksums into output file
        with output_file.open("w") as ofp:
            run(f"{which('sort')} {tempfile.name}", in_stream=False, out_stream=ofp, hide=True)

    return output_file


def checksum_command(base, host, exclude_filename, hash_cmd):
    cmd = f"cd {str(base)}; {which('find', host)} . -type f"
    if exclude_filename:
        cmd += f" | {which('egrep', host)} -v -f {exclude_filename} | xargs -n 1 -I FILE {hash_cmd} 'FILE'"
    else:
        cmd += f" -exec {hash_cmd} \\{{\\}} \\;"
    return cmd


def generate_exclude_file(host, rsync_args):
    patterns = rsync_exclude_patterns(rsync_args)
    if not patterns:
        return ""
    with NamedTemporaryFile("w+", delete=False) as tempfile:
        tempfile.file.write("\n".join(patterns) + "\n")
        tempfile.close()
        cmd = "TEMPFILE=$(mktemp) && cat ->$TEMPFILE && echo $TEMPFILE"
        with Path(tempfile.name).open("r") as ifp:
            proc = runner(host)(cmd, in_stream=ifp, warn=True, hide=True)
        if proc.failed:
            raise ChecksumExcludeFileGenerationFailed(proc.stderr)
        return proc.stdout.strip()


def delete_exclude_file(host, filename):
    runner(host)(f"rm {filename}", hide=True)


def delete_file(filename):
    Path(filename).unlink()


def compare_checksums(src_sums, dst_sums):
    """run diff on hash digest files, return length if identical, otherwise raise exception"""

    diff = run(f"{which('diff')} {str(src_sums)} {str(dst_sums)}", in_stream=False, hide=True, warn=True)
    if diff.failed:
        output_dir = Path(src_sums).parent
        (output_dir / "cptree.diff.out").write_text(diff.stdout)
        (output_dir / "cptree.diff.err").write_text(diff.stderr)
        tempdir = mkdtemp(prefix="cptree")
        shutil.copytree(output_dir, tempdir.name, dirs_exist_ok=True)
        raise ChecksumCompareFailed(f"details written to {tempdir}")
    wc = run(f"{which('wc')} -l {str(src_sums)}", in_stream=False, hide=True)
    return int(wc.stdout.split()[0])
