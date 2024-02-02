# cptree exceptions


class Fail(Exception):
    pass


class InvalidDirectory(Fail):
    pass


class ChecksumCompareFailed(Fail):
    pass
