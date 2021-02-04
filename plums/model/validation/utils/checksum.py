import hashlib


def md5_checksum(filepath):
    """Compute a MD5 checksum of a file.

    Args:
        filepath (Pathlike): The file location.

    Returns:
        str: The MD5 checksum of the file.

    """
    return _hash_bytestr_iter(_file_as_blockiter(open(str(filepath), 'rb')), hashlib.md5(), ashexstr=True)


def _hash_bytestr_iter(bytesiter, hasher, ashexstr=False):
    for block in bytesiter:
        hasher.update(block)
    return hasher.hexdigest() if ashexstr else hasher.digest()


def _file_as_blockiter(afile, blocksize=65536):
    with afile:
        block = afile.read(blocksize)
        while len(block) > 0:
            yield block
            block = afile.read(blocksize)
