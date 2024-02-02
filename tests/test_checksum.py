# checksum test cases

import sys
from pathlib import Path

import pytest
from invoke import run

from cptree.checksum import dst_checksum, src_checksum
from cptree.cptree import cptree

HASH = "sha256"


@pytest.fixture
def datadir():
    return Path("tests/data/output")


@pytest.fixture
def file_list(datadir):
    return datadir / "file_list"


@pytest.fixture
def reference_checksums(datadir):
    return datadir / f"reference.{HASH}"


@pytest.fixture
def output_filename(datadir):
    return str(datadir / f"test.{HASH}")


@pytest.fixture
def compare_checksums(datadir):
    def _compare_checksums(test_sums):
        reference_sums = (datadir / "reference").with_suffix(test_sums.suffix)
        cmd = f"diff -y {str(reference_sums)} {str(test_sums)}"
        result = run(cmd, hide=True, warn=True)
        if result.failed:
            print(result.stdout, flush=True)
            print(result.stderr, file=sys.stderr, flush=True)
        return result.ok

    return _compare_checksums


def test_checksum_local_src(local_src, local_dst, file_list, datadir, compare_checksums):
    test_sums = src_checksum(
        local_src,
        local_dst,
        file_list,
        HASH,
        Path(datadir) / f"local_src.{HASH}",
    )
    assert compare_checksums(test_sums)


def test_checksum_local_dst(local_src, local_dst, file_list, datadir, compare_checksums):
    assert cptree(local_src, local_dst, delete=True, hash=None) == 0
    test_sums = dst_checksum(
        local_src,
        local_dst,
        file_list,
        HASH,
        Path(datadir) / f"local_dst.{HASH}",
    )
    assert compare_checksums(test_sums)


def test_checksum_remote_src(remote_src, local_src, local_dst, file_list, datadir, compare_checksums):
    assert cptree(local_src, remote_src, delete="ask", hash=None) == 0
    test_sums = src_checksum(
        remote_src,
        local_dst,
        file_list,
        HASH,
        Path(datadir) / f"remote_src.{HASH}",
    )
    assert compare_checksums(test_sums)


def test_checksum_remote_dst(local_src, remote_dst, file_list, datadir, compare_checksums):
    assert cptree(local_src, remote_dst, delete="ask", hash=None) == 0
    test_sums = dst_checksum(
        local_src,
        remote_dst,
        file_list,
        HASH,
        Path(datadir) / f"remote_dst.{HASH}",
    )
    assert compare_checksums(test_sums)
