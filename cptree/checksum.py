# generate checksum for a list of files

from pathlib import Path
from tempfile import NamedTemporaryFile

import click
from fabric import Connection
from invoke import run
from tqdm import tqdm

from .common import split_target
from .exceptions import ChecksumCompareFailed, ChecksumGenerationFailed
from .watcher import LineWatcher


def src_checksum(src, dst, hash, output_filename, ascii, width, count):
    return _checksum(True, src, dst, hash, output_filename, ascii, width, count)


def dst_checksum(src, dst, hash, output_filename, ascii, width, count):
    return _checksum(False, src, dst, hash, output_filename, ascii, width, count)


# noqa: C901


def _checksum(is_src, src, dst, hash, output_filename, ascii, width, count):
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

    hproc = runner(f"which 2>/dev/null {hash} || which {hash}sum", hide=True, warn=True)
    if hproc.ok:
        hasher = hproc.stdout.strip()
    else:
        breakpoint()
        pass
    if hasher.endswith("sum"):
        hasher += " --tag"

    options = "--progress"
    if width:
        options += f" --width {width}"
    if ascii:
        options += " --ascii"

    with NamedTemporaryFile("w+", delete_on_close=False) as tempfile:
        with tqdm(total=count, unit=" lines", miniters=1, delay=1, ncols=width, ascii=ascii) as bar:

            def line_callback(line):
                bar.update(1)

            genproc = runner(
                f"cd {target}; find . -type f -exec {hasher} \x5c\x7b\x5c\x7d \x5c;",
                warn=True,
                watchers=[LineWatcher(None, None, line_callback)],
                hide=True,
                out_stream=tempfile.file,
            )

            if genproc.failed:
                raise ChecksumGenerationFailed(genproc.stderr)

        tempfile.close()
        click.echo(f"Sorting {mode} checksums...")
        with Path(output_filename).open("w") as ofp:
            run(f"sort {tempfile.name}", out_stream=ofp, hide=True)

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
