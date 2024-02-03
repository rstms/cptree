# utility functions


def split_target(target: str) -> (str, str):
    """return (hostname, path) for target; hostname is None for local target"""
    host, _, path = str(target).partition(":")
    if path:
        return host, path
    else:
        return None, host


def parse_int(field):
    return int(field.replace(",", ""))
