# hash type tests

import os
import re
from pathlib import Path

import pytest
from fabric import Connection
from invoke import run


@pytest.fixture
def hashes():
    result = run("cptree --help")
    match = re.search(r".*\s--hash\s+\[(.*)\]", result.stdout)
    hlist = match.groups()[0]
    ret = hlist.split("|")
    ret.remove("none")
    return ret


@pytest.fixture
def hosts():
    return os.environ["TEST_HOSTS"].split(",")


def test_hash_hosts(hosts, hashes, local_src):
    local_src = str(Path(local_src).resolve()) + "/"
    for host in hosts:
        assert Connection(host).run("uname -a").ok
        for hash in hashes:
            assert run(
                f"cptree {local_src} {host}:archive/cptree_test --create=force --hash {hash} --output /tmp/test/output"
            ).ok
