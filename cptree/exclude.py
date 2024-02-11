# exclusion list functions

import shlex
from pathlib import Path

from .common import read_file_lines


def rsync_exclude_patterns(rsync_args):
    """parse rsync args and return list of exclude patterns as regex"""
    if not rsync_args:
        return []
    globs = []
    args = shlex.split(rsync_args)
    while "--exclude" in args:
        pos = args.index("--exclude")
        args.pop(pos)
        globs.append(args.pop(pos))
    while "--exclude-from" in args:
        pos = args.index("--exclude-from")
        args.pop(pos)
        globs.extend(read_file_lines(Path(args.pop(pos))))
    patterns = [glob_to_egrep(pattern) for pattern in globs]
    return patterns


def glob_to_egrep(glob_pattern):
    """
    Convert a glob pattern to a regex pattern usable by egrep.

    Args:
    - glob_pattern (str): The glob pattern to convert.

    Returns:
    - str: A regex pattern equivalent to the input glob pattern.
    """
    # Escape special regex characters in glob pattern, except for * and ?
    special_chars = "\\^$+{}[]|()."
    for char in special_chars:
        glob_pattern = glob_pattern.replace(char, "\\" + char)

    # Convert glob wildcards to regex equivalents
    glob_pattern = glob_pattern.replace("*", ".*")
    glob_pattern = glob_pattern.replace("?", ".")

    # Anchor the pattern to match the whole string
    regex_pattern = "^\\./" + glob_pattern + "$"

    return regex_pattern
