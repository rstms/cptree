# cptree implementation

import os
import re
import sys
from pathlib import Path
from typing import Generator

import click
import humanize
from fabric import Connection
from invoke import run
from invoke.watchers import StreamWatcher
from tqdm import tqdm

from .exceptions import InvalidDirectory


def split_target(target):
    host, _, path = target.partition(":")
    if path:
        return True, path, host
    else:
        return False, target, None


def verify_remote_directory(host, target, src, dst, ask_create=False, force_create=False):
    result = Connection(host).run(f"[ -d {target} ]", warn=True)
    if not result.ok:
        if dst:
            if force_create or (
                ask_create and click.confirm(f"{target} does not exist on {host}. Create it?", abort=True)
            ):
                Connection(host).run(f"mkdir -p {target}")
        else:
            raise InvalidDirectory(f"{host}:{target}")


def verify_directory(target, src=False, dst=False, ask_create=False, force_create=False):
    if src:
        dst = False
    elif dst:
        src = False
    else:
        raise RuntimeError

    remote, target, host = split_target(target)
    if remote:
        verify_remote_directory(host, target, src, dst, ask_create=ask_create, force_create=force_create)
    else:
        target = Path(os.path.expanduser(target)).resolve()
        if target.exists() is False:
            if dst:
                if force_create or (ask_create and click.confirm(f"{target} does not exist. Create it?", abort=True)):
                    target.mkdir()
            if target.is_dir() is False:
                raise InvalidDirectory(str(target))


class LineWatcher(StreamWatcher):
    def __init__(self, file_callback, progress_callback, line_callback):
        self.index = 0
        self.file_pattern = re.compile(r"^~([^\s]+)\s([0-9,]+)\s(.*)")
        self.percent_pattern = re.compile(r"^\s*([^\s]+)\s+([0-9\.]+)%")
        self.file_callback = file_callback
        self.progress_callback = progress_callback
        self.line_callback = line_callback
        self.file_count = 0
        self.byte_count = 0
        super().__init__()

    def parse_line(self, line):
        if self.line_callback:
            return self.line_callback(line)
        file = self.file_pattern.match(line)
        if file:
            codes, length, filename = file.groups()
            self.file_count += 1
            return self.file_callback(filename, self.file_count, int(length.replace(",", "")), codes)
        percent = self.percent_pattern.match(line)
        if percent:
            length, progress = percent.groups()
            length = int(length.replace(",", ""))
            chunk = length - self.byte_count
            self.byte_count = length
            return self.progress_callback(chunk, progress)

    def submit(self, stream: str) -> Generator[str, None, None]:
        while True:
            try:
                pos = stream.index("\n", self.index)
            except ValueError:
                try:
                    pos = stream.index("\r", self.index)
                except ValueError:
                    return
            chunk = stream[self.index : pos]  # noqa: E203
            self.index = pos + 1
            chunks = chunk.split("\n")
            for chunk in chunks:
                for line in chunk.split("\r"):
                    if len(line):
                        self.parse_line(line)
        yield ""


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
    scanproc = run(f"rsync -a --list-only {opts} {src} {dst}", hide="both", warn=True)
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
        "d": "dirs",
        "-": "files",
        "l": "links",
        "p": "pipes",
        "c": "char_devs",
        "b": "block_devs",
    }

    size = 0
    files = []
    for item in items:
        fields = item.split()
        if len(fields) < 5:
            raise RuntimeError
        length = fields[1]
        if "," in length:
            length = length.replace(",", "")
        size += int(length)
        file_type = item[0]
        counts[file_type] += 1
        if file_type == "-":
            files.append(fields[4])

    msg = f"Transferring {humanize.naturalsize(size, gnu=True)}"
    for k, v in counts.items():
        if v:
            msg += f" {names[k]}={v}"
    click.echo(msg)
    if (counts["b"] + counts["c"]) > 0:
        click.confirm("Attempting transfer of device nodes.  Are you certain you know what you're doing?", abort=True)

    return size, len(items), files


def checksum(target, file_list, output):
    """read pathnames from file_list, performing hash on target writing to output Path"""

    infile = Path(file_list)
    outfile = Path(output)

    remote, target, host = split_target(target)

    with infile.open('r') as ifp:
        with outfile.open('w') as ofp:

        if remote: 
            raise NotImplementedError
        else:
            proc = run(cmd, in_path = ifp, out_path=ofp)

    return outfile
        

def compare_checksums(src_sums, dst_sums):
    breakpoint()
    return True

def cptree(*args, work_dir=None, **kwargs):
    """call _cptree with work_dir from argument or a temp dir"""

    if work_dir is not None:
        work_dir = Path(work_dir)
        if work_dir.is_dir():
            return _cptree(*args, work_dir=work_dir, **kwargs)
        else:
            raise InvalidDirectory(work_dir)

    with TemporaryDirectory() as temp_dir:
        return _cptree(*args, work_dir=Path(temp_dir), **kwargs)


def _cptree(src, dst, *, ask_create=True, force_create=False, ascii=False, rsync_options=None, disable=False, work_dir=None):

    verify_directory(src, src=True)
    verify_directory(dst, dst=True, ask_create=ask_create, force_create=force_create)

    if rsync_options:
        opts = " ".join(rsync_options)
    else:
        opts = ""

    bytes, items, files = prescan(src, dst, opts)

    file_list = work_dir / 'file_list'
    file_list.write_text('\n'.join(files))

    bar = tqdm(total=bytes, unit="B", unit_scale=True, ascii=ascii, disable=disable)

    def line_callback(line):
        click.echo(line)

    def file_callback(filename, count, length, codes):
        bar.set_description(f"[{count}/{files}]", refresh=False)

    def progress_callback(chunk, progress):
        bar.update(chunk)

    if disable:
        progress_opts = ""
    else:
        progress_opts = "-ii --info PROGRESS2 --out-format '~%i %l %f'"

    cmd = f"rsync -avz {progress_opts} {opts} {src} {dst}"

    proc = run(
        cmd,
        watchers=[LineWatcher(file_callback, progress_callback, line_callback if disable else None)],
        in_stream=None,
        hide="both",
        warn=True,
    )

    bar.close()

    for error in proc.stderr.strip().split("\n"):
        if error:
            click.echo(error, err=True)

    src_sums = checksum(src, file_list, work_dir / 'src.sha256')
    dst_sums = checksum(dst, file_list, work_dir / 'dst.sha256')

    compare_checksums(src_sums, dst_sums)

    return proc.return_code
