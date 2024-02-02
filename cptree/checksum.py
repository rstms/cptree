# generate checksum for a list of files

import hashlib
import io
import os
from pathlib import Path

import click
from fabric import Connection
from invoke import StreamWatcher, run
from tqdm import tqdm

from .exceptions import ChecksumCompareFailed
from .utils import split_target

DEFAULT_HASH = "sha1"


def src_checksum(src, dst, file_list, hash, output_filename):
    return _checksum(True, src, dst, file_list, hash, output_filename)


def dst_checksum(src, dst, file_list, hash, output_filename):
    return _checksum(False, src, dst, file_list, hash, output_filename)


def _checksum(is_src, src, dst, file_list, hash, output_filename):  # noqa: C901
    """generate MD5 hash for each file in target, returning local file containing result"""

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
    if host is None:
        runner = run
    else:
        runner = Connection(host).run

    if hash is None:
        hash = DEFAULT_HASH

    # determine binary to generate checksum (OpenBSD or Linux)
    if runner(f"which {hash}sum", hide=True, warn=True).ok:
        hasher = f"{hash}sum --tag"
    else:
        hasher = hash

    # cmd = f"LIST=$(mktemp); echo $LIST >&2; cat ->$LIST; ls -l $LIST >&2; cd {target}; xargs <$LIST --verbose {hasher}; rm $LIST"
    cmd = f"cd {target}; xargs {hasher}"

    infile = Path(file_list)
    outfile = Path(output_filename)
    filenames = infile.read_text().strip().split("\n")

    click.echo(f"Generating {len(filenames)} {mode} checksums: {label} -> {str(outfile)}")


    hasher = "import sys, os, hashlib, pathlib ;"
    hasher += f'os.chdir("{str(target)}");'
    hasher += '[ sys.stdout.write(f"'
    hasher += hash.upper()
    hasher += " ({name}) = {"
    hasher += f"hashlib.{hash}(pathlib.Path(name).read_bytes()).hexdigest()"
    hasher += '}\\n") or sys.stdout.flush() for name in [n.strip() for n in sys.stdin.readlines()]]'

    cmd = f"python3 -c '{hasher}'"

    
    if False:

        class Watcher(StreamWatcher):
            def __init__(self, callback):
                self.index = 0
                self.callback = callback
                super().__init__()
    
            def submit(self, stream):
                chunk = stream[self.index :]  # noqa: E203
                self.index = len(stream)
                self.callback(chunk)
                yield ""
    
        # source_pipe, sink_pipe = os.pipe2(os.O_NONBLOCK | os.O_CLOEXEC)
        source_pipe, sink_pipe = os.pipe()
        source = os.fdopen(source_pipe, "r")
        sink = os.fdopen(sink_pipe, "w")
        with io.BufferedRWPair(source, sink) as pipe:
            with tqdm(total=len(filenames), unit="hash", miniters=1) as bar, outfile.open("w") as ofp:
    
                def new_chunk(chunk):
                    print(f"chunk: {repr(chunk)}")
                    breakpoint()
    
                proc = runner(
                    cmd, watchers=[Watcher(new_chunk)], in_stream=pipe, out_stream=ofp, asynchronous=True, warn=True
                )
                for filename in filenames:
                    bar.update()
                    sink.write(filename + "\n")
                    sink.flush()
                sink.close()
                result = proc.join()
            source.close()
        if result.failed:
            raise RuntimeError(result.stderr)



    if False:
        input_size = infile.stat().st_size
        with infile.open("r") as ifp, outfile.open("w") as ofp:
            with tqdm.wrapattr(ifp, "read", total=input_size) as tifp:
                runner(cmd, in_stream=tifp, out_stream=ofp, hide="stdout")

    if False:
        filenames = infile.read_text().strip().split("\n")
        with tqdm(total=len(filenames)) as bar, outfile.open("w") as ofp:
            for filename in filenames:
                bar.update()
                file = Path(target) / filename
                digest = getattr(hashlib, hash)(file.read_bytes()).hexdigest()
                line = f"{hash.upper()} ({filename}) {digest}\n"
                ofp.write(line)

    return outfile


def compare_checksums(src_sums, dst_sums):
    """take two pathlike args, returning True if their contents are identical"""

    result = run(f"diff {str(src_sums)} {str(dst_sums)}", hide=True, warn=True)
    if result.failed:
        Path(".cptree.err").write_text(result.stderr)
        Path(".cptree.out").write_text(result.stdout)
        Path(".cptree.src").write_text(Path(src_sums).read_text())
        Path(".cptree.dst").write_text(Path(dst_sums).read_text())
        raise ChecksumCompareFailed("details written to .cptree.*")

    return result.ok
