# checksum test cases

import subprocess
import sys

import pytest
from invoke import run

from cptree.checksum import dst_checksum, src_checksum
from cptree.cptree import cptree

HASH = "sha256"


@pytest.fixture
def output(test_datadir):
    return test_datadir / "output"


@pytest.fixture
def file_list(output):
    return output / "file_list"


@pytest.fixture
def reference_checksums(output):
    return output / f"reference.{HASH}"


@pytest.fixture
def output_filename(output):
    return str(output / f"test.{HASH}")


@pytest.fixture
def count():
    def _count(src_dir):
        ret = int(subprocess.check_output(f"find {src_dir} -type f | wc -l", shell=True, text=True))
        return ret

    return _count


@pytest.fixture
def compare_checksums(output):
    def _compare_checksums(test_sums):
        reference_sums = (output / "reference").with_suffix(test_sums.suffix)
        cmd = f"diff -y {str(reference_sums)} {str(test_sums)}"
        result = run(cmd, hide=True, warn=True)
        if result.failed:
            print(result.stdout, flush=True)
            print(result.stderr, file=sys.stderr, flush=True)
        return result.ok

    return _compare_checksums


def test_checksum_local_src(local_src, local_dst, output, compare_checksums, count):
    test_sums = src_checksum(local_src, local_dst, HASH, output / f"local_src.{HASH}", False, 120, count(local_src))
    assert compare_checksums(test_sums)


def test_checksum_local_dst(local_src, local_dst, output, compare_checksums, count):
    assert cptree(str(local_src) + "/", local_dst, delete="force-no-countdown", hash=None) == 0
    test_sums = dst_checksum(local_src, local_dst, HASH, output / f"local_dst.{HASH}", False, 120, count(local_src))
    assert compare_checksums(test_sums)


def test_checksum_remote_src(remote_src, local_src, local_dst, output, compare_checksums, count):
    assert cptree(str(local_src) + "/", remote_src, delete="force-no-countdown", hash=None) == 0
    test_sums = src_checksum(remote_src, local_dst, HASH, output / f"remote_src.{HASH}", False, 120, count(local_src))
    assert compare_checksums(test_sums)


def test_checksum_remote_dst(local_src, remote_dst, output, compare_checksums, count):
    assert cptree(str(local_src) + "/", remote_dst, delete="force-no-countdown", hash=None) == 0
    test_sums = dst_checksum(local_src, remote_dst, HASH, output / f"remote_dst.{HASH}", False, 120, count(local_src))
    assert compare_checksums(test_sums)
