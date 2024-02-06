# checksum test cases

import subprocess

import pytest
from invoke import run

from cptree.checksum import checksum
from cptree.cptree import cptree

HASH = "sha256"


@pytest.fixture
def output_dir(test_datadir):
    return test_datadir / "output"


@pytest.fixture
def count(local_src):
    return int(subprocess.check_output(f"cd {local_src.rstrip('/')}; find . -type f | wc -l", shell=True, text=True))


@pytest.fixture
def kwargs(count):
    return dict(total=count, disable=False, ascii=True, ncols=120, miniters=1)


@pytest.fixture
def compare_checksums(output_dir, count):
    def _compare_checksums(test_sums):
        reference_sums = (output_dir / "reference").with_suffix(test_sums.suffix)
        cmd = f"diff -y {str(reference_sums)} {str(test_sums)}"
        result = run(cmd, hide=True, warn=True)
        if result.failed:
            assert False, dict(stdout=result.stdout.split("\n"), stderr=result.stderr.split("\n"))
        return True

    return _compare_checksums


def test_checksum_local_src(local_src, local_dst, output_dir, compare_checksums, kwargs):
    test_sums = checksum(local_src, HASH, output_dir / f"local.src.{HASH}", kwargs, src=True)
    assert compare_checksums(test_sums)


def test_checksum_local_dst(local_src, local_dst, output_dir, compare_checksums, kwargs):
    assert cptree(local_src, local_dst, delete="force-no-countdown", hash=None) == 0
    test_sums = checksum(local_dst, HASH, output_dir / f"local.dst.{HASH}", kwargs, dst=True)
    assert compare_checksums(test_sums)


def test_checksum_remote_src(remote_src, local_src, local_dst, output_dir, compare_checksums, kwargs):
    assert cptree(local_src, remote_src, delete="force-no-countdown", hash=None) == 0
    test_sums = checksum(remote_src, HASH, output_dir / f"remote.src.{HASH}", kwargs, src=True)
    assert compare_checksums(test_sums)


def test_checksum_remote_dst(local_src, remote_dst, output_dir, compare_checksums, kwargs):
    assert cptree(local_src, remote_dst, delete="force-no-countdown", hash=None) == 0
    test_sums = checksum(remote_dst + "/", HASH, output_dir / f"remote.dst.{HASH}", kwargs, dst=True)
    assert compare_checksums(test_sums)
