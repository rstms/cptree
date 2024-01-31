# cptree implementation

import os
from pathlib import Path

import click
from fabric import Connection

from .exceptions import InvalidDirectory


def verify_remote_directory(host, target, src, dst, ask_create):
    result = Connection(host).run(f"[ -d {target} ]", warn=True)
    if not result.ok:
        if dst and ask_create and click.confirm(f"{target} does not exist on {host}. Create it?", abort=True):
            Connection(host).run(f"mkdir -p {target}")
        else:
            raise InvalidDirectory(f"{host}:{target}")


def verify_directory(target, src=False, dst=False, ask_create=False):
    if src:
        dst = False
    elif dst:
        src = False
    else:
        raise RuntimeError

    remote = ":" in target
    host = None
    if remote:
        host, _, target = target.partition(":")
        verify_remote_directory(host, target, src, dst, ask_create)
    else:
        target = Path(os.path.expanduser(target)).resolve()
        if target.exists() is False:
            if dst and ask_create and click.confirm(f"{target} does not exist. Create it?", abort=True):
                target.mkdir()
            if target.is_dir() is False:
                raise InvalidDirectory(str(target))

    return target, remote, host


def verify_src_directory(target):
    return verify_directory(target, src=True)


def verify_dst_directory(target, ask_create):
    return verify_directory(target, dst=True, ask_create=ask_create)


def cptree(src, dst, ask_create=False):
    remote_src = ":" in src
    remote_dst = ":" in dst
    src, remote_src, src_host = verify_src_directory(src)
    dst, remote_dst, dst_host = verify_dst_directory(dst, ask_create)
    click.echo(f"rsync {src} {dst}")
    return 0
