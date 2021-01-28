"""
Shared utilities for testing implementations.
"""
import pathlib
import typing
import hashlib

def file_summary(path: pathlib.Path) -> typing.Tuple[int, str]:
    """Reads a file off disk, and returns the size of the file and the sha256
    hash of it.

    Args:
        path -- A path to a file that should be summarized.

    Return:
        Two values, first the size of the file, in bytes, and second, the
        sha256 hex digest of the contents of the file.
    """
    with open(path, 'rb') as handle:
        data: bytes = handle.read()
        data_len: int = len(data)
        hasher = hashlib.sha256()
        hasher.update(data)
        hash_hex: str = hasher.hexdigest()
    return data_len, hash_hex
