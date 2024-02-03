# generate checksum for a list of files

from pathlib import Path

import click

# from fabric import Connection
from invoke import run
from tqdm import tqdm

from .common import split_target
from .exceptions import ChecksumCompareFailed
from .hash import HashDigest


def src_checksum(src, dst, file_list, hash, output_filename):
    return _checksum(True, src, dst, file_list, hash, output_filename)


def dst_checksum(src, dst, file_list, hash, output_filename):
    return _checksum(False, src, dst, file_list, hash, output_filename)


def _checksum(is_src, src, dst, file_list, hash, output_filename):  # noqa: C901
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

    # configure local or remote runner
    if host:
        raise NotImplementedError

    infile = Path(file_list)
    outfile = Path(output_filename)

    click.echo(f"Generating {mode} checksums for {label}")

    with tqdm(total=infile.stat().st_size, unit="bytes", unit_scale=True) as bar:
        hasher = HashDigest(target, hash)
        with infile.open("r") as ifp, outfile.open("w") as ofp:
            while True:
                filename = ifp.readline()
                if filename:
                    bar.update(len(filename))
                    digest = hasher.file_digest(filename.strip())
                    ofp.write(digest + "\n")
                else:
                    break

    return outfile


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
