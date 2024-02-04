# verify directory existence

import os
from pathlib import Path
from time import sleep

import click
from fabric import Connection
from invoke import run

from .common import split_target
from .exceptions import InvalidDirectory

DELETE_COUNTDOWN = 10


def _verify_directory(host, target, dir_type, create=None, delete=None):
    target = str(target)
    if host:
        label = f"Remote {dir_type} {host}:{target}"
        runner = Connection(host).run
        if dir_type == "output":
            raise InvalidDirectory("Unsupported: " + label)
        if "~" in str(target):
            raise InvalidDirectory("Illegal '~' expansion: " + label)
    else:
        if "~" in str(target):
            target = os.path.expanduser(str(target))
            target = str(Path(target).resolve())
        label = f"Local {dir_type} {target}"
        runner = run

    result = runner(f"[ -d {target} ]", warn=True, hide=True)
    if result.failed:
        # doesn't exist, check for create
        if (dir_type in ["destination", "output"]) and (create in ["ask", "force", True]):
            if create == "ask":
                click.confirm(f"{label} does not exist. Create it?", abort=True)
            runner(f"mkdir -p {target}", echo=True)
        elif dir_type != "destination":
            # not created, all but DST must exist
            raise InvalidDirectory(label)
    else:
        # exists, check for delete request
        if (dir_type in ["destination", "output"]) and delete in [
            "ask",
            "force",
            "force-no-countdown",
            True,
        ]:
            cmd = confirm_delete(target, label, host, delete)
            runner(cmd, echo=True)


def confirm_delete(target, label, host, delete):
    cmd = f"rm -rf {target}"
    if delete == "ask":
        click.confirm(f"Delete {label}?", abort=True)
    if delete != "force-no-countdown":
        delete_countdown(label, cmd, host)
    return cmd


def delete_countdown(msg, cmd, host):
    click.echo(f"\nCAUTION: About to delete {msg}")
    click.echo(f"\nExecuting '{cmd}' on {host or 'localhost'} in ", nl=False)
    for count in range(DELETE_COUNTDOWN, 0, -1):
        click.echo(f"{count}...", nl=False)
        sleep(1)


def verify_output_directory(target):
    host, target = split_target(target)
    return _verify_directory(host, target, "output", "ask", None)


def verify_src_directory(target):
    host, target = split_target(target)
    return _verify_directory(host, target, "source", None, None)


def verify_dst_directory(target, create=None, delete=None):
    if delete:
        create = None
    host, target = split_target(target)
    # verify parent of DST dir exists
    _verify_directory(host, Path(target).parent, "destination", create, False)
    if delete:
        # delete target dir
        _verify_directory(host, target, "destination", None, delete)
