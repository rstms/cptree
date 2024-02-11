# utility functions

import os
import re
from pathlib import Path

import fabric
import invoke

from .exceptions import CommandNotFound

OS_COMMAND_MAP = {"which": {"linux": "which", "win": "where", "openbsd": "which"}}

OS_BASE = re.compile(r"([^0-9]+)")


def map_cmd(command):
    platform = os.sys.platform
    match = OS_BASE.match(platform)
    base = match.groups()[0]
    return OS_COMMAND_MAP[command][base]


def split_target(target: str) -> (str, str):
    """return (hostname, path) for target; hostname is None for local target"""
    host, _, path = str(target).partition(":")
    if path:
        return host, path
    else:
        return None, host


def parse_int(field):
    return int(field.replace(",", ""))


def read_file_lines(filename, strip=True):
    with Path(filename).open("r") as ifp:
        for line in ifp.readlines():
            if strip:
                line = line.strip()
            if line:
                yield line


def write_file_lines(dir, name, lines):
    dir = Path(dir)
    if not dir.is_dir():
        dir.mkdir()
    file = dir / name
    if isinstance(lines, (list, tuple)):
        lines = "\n".join(lines)
    if lines:
        lines = lines.rstrip("\n") + "\n"
    file.write_text(lines)


def runner(host):
    return fabric.Connection(host).run if host else invoke.run


def host_mode(host):
    return "remote" if host else "local"


def which(command, host=None, quiet=False):
    """return local or remote command path if valid, otherwise raise exception or optionally return None"""
    probe = runner(host)(f"{map_cmd('which')} {command}", in_stream=False, hide=True, warn=True)
    cmd = probe.stdout.strip()
    if probe.ok and cmd:
        return cmd
    elif quiet:
        return None
    else:
        raise CommandNotFound(f"{command} not available on {host_mode(host)}")
