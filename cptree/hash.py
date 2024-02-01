# generate a command using local system python to hash a file


# read a list of pathnames on stdin, write hash_digest, path to stdout
HASHCODE = "import hashlib,sys;[print(hashlib.md5(open(file,'rb').read()).hexdigest(), file) for file in sys.stdin.read().splitlines()]"


def hash_command():
    quoted = "'\"" + HASHCODE + "\"'"
    return f"python -c {quoted}"
