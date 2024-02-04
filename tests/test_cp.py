# directory tests

import pytest
from invoke import run

from cptree import cptree
from cptree.exceptions import InvalidDirectory, RsyncTransferFailed


@pytest.fixture(autouse=True)
def delete_local_dst(local_dst):
    print()
    cmd = f"rm -rf {local_dst}"
    run(cmd)


# def test_cp_dev():
#    ret = cptree("/dev", "/tmp/dev", force_create=True)
#    assert ret == 0


def test_cp_local_local(local_src, local_dst):
    ret = cptree(local_src, local_dst, create=True, delete="force-no-countdown")
    assert ret == 0


def test_cp_local_remote(local_src, remote_dst):
    ret = cptree(local_src, remote_dst, create=True, delete="force-no-countdown")
    assert ret == 0


def test_cp_remote_local(remote_src, local_dst):
    ret = cptree(remote_src, local_dst, create=True, delete="force-no-countdown")
    assert ret == 0


def test_cp_badlocal_badlocal():
    with pytest.raises(InvalidDirectory):
        cptree("bad_local_src", "/bad_local_dst", create=None, delete=None)


def test_cp_local_badlocal(local_src):
    with pytest.raises(RsyncTransferFailed):
        cptree(local_src, "/bad_local_dst", create=None, delete=None)


def test_cp_badlocal_local(local_dst):
    with pytest.raises(InvalidDirectory):
        cptree("bad_local_src", local_dst, create=True, delete="force-no-countdown")


def test_cp_badremote_local(remote_host, local_dst):
    bad_remote_src = f"{remote_host}:bad_remote_src"
    with pytest.raises(InvalidDirectory):
        cptree(bad_remote_src, local_dst, create=True, delete="force-no-countdown")


def test_cp_local_badremote(local_src, remote_host):
    bad_remote_dst = f"{remote_host}:/bad_remote_dst"
    with pytest.raises(RsyncTransferFailed):
        cptree(local_src, bad_remote_dst, create=False, delete=False)


def test_cp_progress(big_local_src, remote_dst, test_datadir):
    cptree(big_local_src, remote_dst, create=None, delete="force", hash="sha256", output_dir=test_datadir / "output")
