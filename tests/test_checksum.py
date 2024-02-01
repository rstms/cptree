# import pytest

from cptree.cptree import checksum


def test_checksum_returns_stub():
    """Test that the checksum function returns ['stub'] for any input."""
    assert checksum("any_target", ["any_file"]) == ["stub"], "Checksum function should return ['stub']"
