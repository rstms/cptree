# global test config

import os
from pathlib import Path

import pytest


@pytest.fixture
def remote_host():
    return os.environ["TEST_REMOTE_HOST"]


@pytest.fixture
def remote_user():
    return os.environ["TEST_REMOTE_USER"]


@pytest.fixture
def remote_dir():
    return os.environ["TEST_REMOTE_DIR"]


@pytest.fixture
def test_datadir():
    return Path(os.environ["TEST_DATA_DIR"])


@pytest.fixture
def local_src(test_datadir):
    return str(test_datadir / "src") + "/"


@pytest.fixture
def local_dst(test_datadir):
    return str(test_datadir / "dst")


@pytest.fixture
def remote_src(remote_user, remote_host, remote_dir):
    return f"{remote_user}@{remote_host}:{remote_dir}/src/"


@pytest.fixture
def remote_dst(remote_user, remote_host, remote_dir):
    return f"{remote_user}@{remote_host}:{remote_dir}/dst"


@pytest.fixture
def big_local_src():
    dir = str(Path(os.environ["TEST_BIG_SRC"]).resolve())
    if dir[-1] != "/":
        dir += "/"
    return dir
