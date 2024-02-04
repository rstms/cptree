# generate checksum for a list of files

from pathlib import Path

import click
from fabric import Connection
from invoke import run

from .common import split_target
from .exceptions import ChecksumCompareFailed, ChecksumGenerationFailed


def src_checksum(src, dst, hash, output_filename, ascii=None, width=None):
    return _checksum(True, src, dst, hash, output_filename, ascii, width)


def dst_checksum(src, dst, hash, output_filename, ascii=None, width=None):
    return _checksum(False, src, dst, hash, output_filename, ascii, width)


# noqa: C901


def _checksum(is_src, src, dst, hash, output_filename, ascii, width):
    """generate BSD-style checksum for each file in target, returning local file containing result"""

    if is_src:
        host, target = split_target(src)
        mode = "source"
    else:
        host, target = split_target(dst)
        _, src_target = split_target(src)
        # target = str(Path(target) / Path(src_target).stem)
        mode = "destination"

    if host:
        label = f"{host}:{target}"
    else:
        label = target
        target = Path(target).resolve()

    click.echo(f"Generating {mode} checksums for {label}")

    if host:
        runner = Connection(host).run
    else:
        runner = run

    options = "--progress"
    if width:
        options += f" --width {width}"
    if ascii:
        options += " --ascii"

    with Path(output_filename).open("w") as ofp:
        proc = runner(
            f"python3 -m hashtree --find --sort-files --base-dir {target} {options}",
            out_stream=ofp,
            warn=True,
        )
        if proc.failed:
            raise ChecksumGenerationFailed(proc.stderr)

    return Path(output_filename)


def compare_checksums(src_sums, dst_sums):
    """take two pathlike args, returning True if their contents are identical"""

    result = run(f"diff {str(src_sums)} {str(dst_sums)}", hide=True, warn=True)
    if result.failed:
        Path(".checksums.src").write_text(Path(src_sums).read_text())
        Path(".checksums.dst").write_text(Path(dst_sums).read_text())
        Path(".checksums.out").write_text(result.stdout)
        Path(".checksums.err").write_text(result.stderr)
        raise ChecksumCompareFailed("details written to .checksums.*")

    return result.ok
