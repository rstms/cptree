# cptree exceptions


class Fail(Exception):
    pass


class InvalidDirectory(Fail):
    pass


class ChecksumCompareFailed(Fail):
    pass


class RsyncTransferFailed(Fail):
    pass


class ChecksumGenerationFailed(Fail):
    pass
