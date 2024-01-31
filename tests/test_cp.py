# directory tests

import pytest
from fabric import Connection
from invoke import run

from cptree import cptree
from cptree.exceptions import InvalidDirectory


@pytest.fixture(autouse=True)
def delete_local_dst(local_dst):
    print()
    cmd = f"rm -rf {local_dst}"
    run(cmd)


# def test_cp_dev():
#    ret = cptree("/dev", "/tmp/dev", force_create=True)
#    assert ret == 0


def test_cp_local_local(local_src, local_dst):
    ret = cptree(local_src, local_dst, force_create=True)
    assert ret == 0


def test_cp_local_remote(local_src, remote_target):
    ret = cptree(local_src, remote_target, force_create=True)
    assert ret == 0


def test_cp_remote_local(remote_target, local_dst):
    ret = cptree(remote_target, local_dst, force_create=True)
    assert ret == 0


def test_cp_badlocal_badlocal():
    with pytest.raises(InvalidDirectory):
        cptree("bad_local_src", "bad_local_dst")


def test_cp_local_badlocal(local_src):
    with pytest.raises(InvalidDirectory):
        cptree(local_src, "bad_local_dst", ask_create=False)


def test_cp_badlocal_local(local_dst):
    with pytest.raises(InvalidDirectory):
        cptree("bad_local_src", local_dst, force_create=True)


def test_cp_badremote_local(remote_host, local_dst):
    bad_remote_src = f"{remote_host}:bad_remote_src"
    with pytest.raises(InvalidDirectory):
        cptree(bad_remote_src, local_dst, ask_create=False, force_create=False)


def test_cp_local_badremote(local_src, remote_host):
    bad_remote_dst = f"{remote_host}:bad_remote_dst"
    with pytest.raises(InvalidDirectory):
        cptree(local_src, bad_remote_dst, ask_create=False, force_create=False)


def test_cp_tqdm(remote_host):
    Connection(remote_host).run("rm -rf cptree")
    cptree("~/src/seven-testnet", "rigel:cptree/foo/moo", force_create=True)
