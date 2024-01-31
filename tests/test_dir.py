# directory tests

import pytest

from cptree import cptree
from cptree.exceptions import InvalidDirectory


def test_dir_local_local(local_src, local_dst):
    ret = cptree(local_src, local_dst)
    assert ret == 0


def test_dir_local_remote(local_src, remote_dst):
    ret = cptree(local_src, remote_dst)
    assert ret == 0


def test_dir_remote_local(remote_src, local_dst):
    ret = cptree(remote_src, local_dst)
    assert ret == 0


def test_dir_badlocal_badlocal():
    with pytest.raises(InvalidDirectory):
        cptree("bad_local_src", "bad_local_dst")


def test_dir_local_badlocal(local_src):
    with pytest.raises(InvalidDirectory):
        cptree(local_src, "bad_local_dst")


def test_dir_badlocal_local(local_dst):
    with pytest.raises(InvalidDirectory):
        cptree("bad_local_src", local_dst)


def test_dir_badremote_local(remote_host, local_dst):
    bad_remote_src = f"{remote_host}:bad_remote_src"
    with pytest.raises(InvalidDirectory):
        cptree(bad_remote_src, local_dst)


def test_dir_local_badremote(local_src, remote_host):
    bad_remote_dst = f"{remote_host}:bad_remote_dst"
    with pytest.raises(InvalidDirectory):
        cptree(local_src, bad_remote_dst, ask_create=False)
