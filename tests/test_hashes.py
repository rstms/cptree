# hash type tests

import re
from pathlib import Path

import pytest
from fabric import Connection
from invoke import run

from cptree.cptree import cptree


@pytest.fixture
def hashes():
    result = run("cptree --help")
    match = re.search(r".*\s--hash\s+\[(.*)\]", result.stdout)
    hlist = match.groups()[0]
    ret = hlist.split("|")
    ret.remove("none")
    return ret


def test_hash_hosts(test_hosts, hashes, local_src):
    local_src = str(Path(local_src).resolve()) + "/"
    for host in test_hosts:
        assert Connection(host).run("uname -a").ok
        for hash in hashes:
            ret = cptree(
                local_src, f"{host}:archive/cptree_test", create="force", hash=hash, output_dir="/tmp/test/output"
            )
            assert ret == 0
            """
            cmd = (
                f"cptree {local_src} {host}:archive/cptree_test"
                f" --create=force --hash {hash}"
                " --output_dir /tmp/test/output"
            )
            proc = run(cmd, warn=True)
            assert proc.ok
            """
