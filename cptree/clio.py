"""CLIO command line infile/outfile handler"""

import sys
from pathlib import Path


class CLIO:
    def __init__(self, infile=None, outfile=None, binary=False):
        self.opened = []
        self.infile = infile
        self.outfile = outfile
        if binary:
            self.imode = "rb"
            self.omode = "wb"
        else:
            self.imode = "r"
            self.omode = "w"

    def __enter__(self):
        if self.infile in ["-", None]:
            self.ifp = sys.stdin
        else:
            self.ifp = Path(self.infile).open(self.imode)
            self.opened.insert(0, self.ifp)
        if self.outfile in ["-", None]:
            self.ofp = sys.stdout
        else:
            self.ofp = Path(self.outfile).open(self.omode)
            self.opened.insert(0, self.ofp)
        return self

    def __exit__(self, *args):
        for stream in self.opened:
            stream.close()
        self.opened = []
        return False
