# invoke watcher

import re
from typing import Generator

from invoke.watchers import StreamWatcher

from .common import parse_int


class LineWatcher(StreamWatcher):
    def __init__(self, *, file_callback=None, progress_callback=None, line_callback=None):
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
            return self.file_callback(filename, self.file_count, parse_int(length), codes)
        percent = self.percent_pattern.match(line)
        if percent:
            length, progress = percent.groups()
            length = parse_int(length)
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
