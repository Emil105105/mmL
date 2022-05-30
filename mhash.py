

def sha256(obj: bytes) -> bytes:
    """
    hash any bytes with sha3-256

    :param obj: bytes object
    :return: the hash
    """
    from hashlib import sha3_256
    h = sha3_256()
    h.update(obj)
    return h.digest()


def sha512(obj: bytes) -> bytes:
    """
    hash any bytes with sha3-512

    :param obj: bytes object
    :return: the hash
    """
    from hashlib import sha3_512
    h = sha3_512()
    h.update(obj)
    return h.digest()


def any_hash(obj: bytes, length: int = 16, iterations: int = 1) -> bytes:
    """
    hash any bytes to any length with a modified version of sha3-512

    :param obj: bytes object
    :param length: length in bytes of the hash
    :param iterations: number of iterations
    :return: the hash
    """
    try:
        from mmath import bytes_xor
    except (ImportError, ModuleNotFoundError):
        from mmL.mmath import bytes_xor
    h = b''
    for i in range(iterations):
        h = sha512(obj)
        while len(h) < length:
            h += sha512(bytes_xor(sha512(obj), h, True))
        obj = h
    return h[0:length]
