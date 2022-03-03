

def sha256(obj: bytes) -> bytes:
    from hashlib import sha3_256
    h = sha3_256()
    h.update(obj)
    return h.digest()


def sha512(obj: bytes) -> bytes:
    from hashlib import sha3_512
    h = sha3_512()
    h.update(obj)
    return h.digest()
