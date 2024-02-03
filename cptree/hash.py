# generate BSD-style checksums for a list of files

# pure python cli

import hashlib
from pathlib import Path

HASHES = hashlib.algorithms_guaranteed

DEFAULT_HASH = "sha256"


class HashDigest:
    def __init__(self, base_path=None, hash=None):
        self.set_base_path(base_path)
        self.set_hash(hash)

    def set_base_path(self, path=None):
        if path is None:
            path = "."
        self.base_path = Path(path)

    def set_hash(self, hash=None):
        if hash is None:
            hash = DEFAULT_HASH
        self._hash = getattr(hashlib, hash.lower())
        self.hash = hash.upper()

    def file_digest(self, filename):
        file = self.base_path / filename
        digest = self._hash(file.read_bytes()).hexdigest()
        return f"{self.hash} ({filename}) = {digest}"
