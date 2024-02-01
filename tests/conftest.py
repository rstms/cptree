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
def local_src():
    return "tests/data/src"


@pytest.fixture
def local_dst():
    return "tests/data/dst"


@pytest.fixture
def remote_target(remote_user, remote_host):
    return f"{remote_user}@{remote_host}:cptree_test"
