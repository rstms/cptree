# global test config

import os

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
def local_src():
    return "tests/data/src"


@pytest.fixture
def local_dst():
    return "tests/data/dst"


@pytest.fixture
def remote_src(remote_user, remote_host, remote_dir):
    return f"{remote_user}@{remote_host}:{remote_dir}/src/"


@pytest.fixture
def remote_dst(remote_user, remote_host, remote_dir):
    return f"{remote_user}@{remote_host}:{remote_dir}/dst"


@pytest.fixture
def big_local_src():
    return os.environ["TEST_BIG_SRC"]
