import io
import sys
from pathlib import Path

from tqdm import tqdm


class ProgressReader:
    def __init__(self, in_stream, **kwargs):
        self.tqdm = None
        self.buffer = ""
        kwargs.setdefault("miniters", 1)

        if in_stream.seekable():
            head = in_stream.tell()
            tail = in_stream.seek(0, io.SEEK_END)
            in_stream.seek(head, io.SEEK_SET)
            kwargs.setdefault("total", tail - head)
            kwargs.setdefault("unit", " bytes")
            kwargs.setdefault("unit_scale", True)
            self.count = 0
        else:
            kwargs.setdefault("unit", " lines")
            self.count = None
        self.kwargs = kwargs
        self.in_stream = in_stream

    def __enter__(self):
        self.tqdm = tqdm(**self.kwargs)
        return self

    def __exit__(self, *args):
        if self.tqdm is not None:
            self.tqdm.close()
            self.tqdm = None
        return False

    def _update(self, len):
        if self.tqdm.total:
            self.tqdm.update(len + 1)
        else:
            self.tqdm.update(1)

    def readlines(self):
        while True:
            chunk = self.in_stream.readline()
            self.buffer += chunk
            while "\n" in self.buffer:
                line, _, self.buffer = self.buffer.partition("\n")
                self._update(len(line))
                yield line
            if not chunk:
                if self.buffer:
                    self._update(len(self.buffer))
                    yield self.buffer
                return


if __name__ == "__main__":
    import time

    import click

    @click.command("progress")
    @click.option("-d", "--delay", type=float)
    @click.argument("INFILE", type=click.Path(dir_okay=False, readable=True), default="-")
    @click.argument("OUTFILE", type=click.Path(dir_okay=False, writable=True), default="-")
    def progress(delay, infile, outfile):
        """progress test cli"""

        closers = []

        if infile in ["-", None]:
            infile = sys.stdin
        else:
            infile = Path(infile).open("r")
            closers.insert(0, infile)
        if infile in ["-", None]:
            outfile = sys.stdout
        else:
            outfile = Path(outfile).open("w")
            closers.insert(0, outfile)

        try:
            with ProgressReader(infile) as reader:
                for line in reader.lines():
                    outfile.write(line + "\n")
                    if delay:
                        time.sleep(delay)
        finally:
            for closer in closers:
                closer.close()

    sys.exit(progress())
