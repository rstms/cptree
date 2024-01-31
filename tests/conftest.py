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
def local_src():
    return str(Path(".") / "cptree")


@pytest.fixture
def local_dst():
    return "tests/data/dst"


@pytest.fixture
def remote_target(remote_user, remote_host):
    return f"{remote_user}@{remote_host}:cptree_test"


@pytest.fixture
def remote_src(remote_target):
    return remote_target + "/src"


@pytest.fixture
def remote_dst(remote_target):
    return remote_target + "/dst"
