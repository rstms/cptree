# test globbing with exclude list

import shutil

import pytest
from fabric import Connection
from invoke import run

from cptree.common import split_target
from cptree.cptree import cptree

from .conftest import _test_targets


@pytest.fixture
def exclude_file(shared_datadir):
    return shared_datadir / "exclude_patterns"


@pytest.fixture
def make_rsync_args(exclude_file):
    def _make_rsync_args(file=False, args=False):
        ret = ""
        if file:
            ret += f" --exclude-from {str(exclude_file)}"
        if args:
            ret += " --exclude 'docs/*' --exclude README.md"
        return ret

    return _make_rsync_args


@pytest.fixture
def files_in_dir():
    def _files_in_dir(dir):
        host, dir = split_target(dir)
        if host:
            runner = Connection(host).run
        else:
            runner = run
        cmd = f"cd {str(dir)}; find . -type f"
        proc = runner(cmd, hide=True, warn=True)
        assert proc.ok
        files = proc.stdout.strip().split("\n")
        return sorted(files)

    return _files_in_dir


@pytest.fixture
def rsync_results(shared_datadir, make_rsync_args, local_src, files_in_dir):
    def _rsync_results(file=False, args=False):
        exclude_file = shared_datadir / "exclude_patterns"
        assert exclude_file.is_file()
        dst = shared_datadir / "rsync_dst"
        shutil.rmtree(dst, ignore_errors=True)
        dst.mkdir()
        rsync_args = make_rsync_args(file, args)
        cmd = f"rsync -avz {local_src} {str(dst)}/ {rsync_args}"
        proc = run(cmd, hide=True, warn=True)
        assert proc.ok
        return files_in_dir(dst)

    return _rsync_results


def _files_in_file(file):
    return sorted(file.read_text().strip().split("\n"))


@pytest.fixture
def expected_none(shared_datadir):
    return _files_in_file(shared_datadir / "expected_exclude_none")


@pytest.fixture
def expected_args(shared_datadir):
    return _files_in_file(shared_datadir / "expected_exclude_args")


@pytest.fixture
def expected_file(shared_datadir):
    return _files_in_file(shared_datadir / "expected_exclude_file")


@pytest.fixture
def expected_both(shared_datadir):
    return _files_in_file(shared_datadir / "expected_exclude_both")


@pytest.mark.parametrize("dst", _test_targets)
def test_glob_none(local_src, dst, output_dir, rsync_results, files_in_dir, expected_none):
    ret = cptree(local_src, dst, create=True, delete="force-no-countdown", hash="md5", output_dir=output_dir)
    assert ret == 0
    assert files_in_dir(dst) == rsync_results()
    assert files_in_dir(dst) == expected_none


@pytest.mark.parametrize("dst", _test_targets)
def test_glob_args(
    shared_datadir, local_src, dst, output_dir, make_rsync_args, rsync_results, files_in_dir, expected_args
):
    rsync_args = make_rsync_args(args=True)
    ret = cptree(
        local_src,
        dst,
        create=True,
        delete="force-no-countdown",
        rsync_args=rsync_args,
        hash="md5",
        output_dir=output_dir,
    )
    assert ret == 0
    assert files_in_dir(dst) == rsync_results(args=True)
    assert files_in_dir(dst) == expected_args


@pytest.mark.parametrize("dst", _test_targets)
def test_glob_file(
    shared_datadir, local_src, dst, output_dir, make_rsync_args, rsync_results, files_in_dir, expected_file
):
    rsync_args = make_rsync_args(file=True)
    ret = cptree(
        local_src,
        dst,
        create=True,
        delete="force-no-countdown",
        rsync_args=rsync_args,
        hash="md5",
        output_dir=output_dir,
    )
    assert ret == 0
    assert files_in_dir(dst) == rsync_results(file=True)
    assert files_in_dir(dst) == expected_file


@pytest.mark.parametrize("dst", _test_targets)
def test_glob_both(
    shared_datadir, local_src, dst, output_dir, make_rsync_args, rsync_results, files_in_dir, expected_both
):
    rsync_args = make_rsync_args(args=True, file=True)
    ret = cptree(
        local_src,
        dst,
        create=True,
        delete="force-no-countdown",
        rsync_args=rsync_args,
        hash="md5",
        output_dir=output_dir,
    )
    assert ret == 0
    assert files_in_dir(dst) == rsync_results(file=True, args=True)
    assert files_in_dir(dst) == expected_both
