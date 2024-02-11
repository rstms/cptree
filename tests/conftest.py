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


@pytest.fixture
def exclude_args():
    return "--exclude */tests/* --exclude ./make/*"


@pytest.fixture
def exclude_file(shared_datadir):
    exfile = shared_datadir / "test_excludes"
    with exfile.open("w") as ofp:
        ofp.write("./docs/*\n")
        ofp.write("./README*\n")
    return f"--exclude-from {str(exfile)}"


@pytest.fixture
def exclude_both(exclude_args, exclude_file):
    return exclude_args + " " + exclude_file


@pytest.fixture
def output_dir(test_datadir):
    return test_datadir / "output"


@pytest.fixture
def test_hosts():
    return os.environ["TEST_HOSTS"].split(",")


_test_targets = [
    f"{os.environ['TEST_REMOTE_USER']}@{host}:{os.environ['TEST_REMOTE_DIR']}"
    for host in os.environ["TEST_HOSTS"].split(",")
]


@pytest.fixture
def test_targets():
    return _test_targets
