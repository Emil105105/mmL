

def generate_rsa_keys(length: int = 2048, exponent: int = None) -> [int, int, int]:
    """
    generate keys for the rsa cryptosystem

    :param length: the length of the modulo in bits (base 2) (HAS to be a multiple of 2!)
    :param exponent: Optional: use custom exponent, for example: 65537
    :return: [e, d, n]: e and n are public, d is a secret
    """
    if length % 2 == 1:
        raise ValueError('Length has to be a multiple of 2')
    try:
        from mrandom import random_prime
    except (ImportError, ModuleNotFoundError):
        from mmL.mrandom import random_prime
    p = random_prime(length // 2)
    q = random_prime(length // 2)
    while q == p:
        q = random_prime(length // 2)
    n = p * q
    phi_n = (p - 1) * (q - 1)
    if exponent is None:
        e = random_prime(length // 2)
        while phi_n % e == 0 or n % e == 0:
            e = random_prime(length // 2)
    else:
        if phi_n % exponent == 0 or n % exponent == 0:
            raise ValueError('It is not possible to use e=' + str(exponent) + ' as an exponent for p=' + str(p) +
                             ' and q=' + str(q) + ' .')
        else:
            e = exponent
    d = pow(e, -1, phi_n)
    return [e, d, n]


def rsa_encrypt(data: int, e: int, n: int) -> int:
    """
    encrypt data with the rsa cryptosystem (rsa_fernet_encrypt is more secure and supports more data)

    :param data: the plaintext
    :param e: public key (e) of the other person
    :param n: public key (n) of the other person
    :return: the ciphertext
    """
    if data > n:
        raise OverflowError('')
    return pow(data, e, n)


def rsa_decrypt(cipher: int, d: int, n: int) -> int:
    """
    decrypt ciphers with the rsa cryptosystem

    :param cipher: the ciphertext
    :param d: your private key
    :param n: your public key (n)
    :return: the plaintext
    """
    return pow(cipher, d, n)


def generate_fernet_key() -> bytes:
    """
    generate a key for the fernet cryptosystem

    :return: the key
    """
    try:
        from cryptography.fernet import Fernet
    except (ImportError, ModuleNotFoundError):
        from subprocess import check_call
        from sys import executable
        check_call([executable, '-m', 'pip', 'install', 'cryptography'])
        from cryptography.fernet import Fernet
    return Fernet.generate_key()


def fernet_encrypt(data: bytes, key: bytes) -> bytes:
    """
    encrypt data with the fernet cryptosystem

    :param data: the plaintext
    :param key: the key
    :return: the cipher
    """
    try:
        from cryptography.fernet import Fernet
    except (ImportError, ModuleNotFoundError):
        from subprocess import check_call
        from sys import executable
        check_call([executable, '-m', 'pip', 'install', 'cryptography'])
        from cryptography.fernet import Fernet
    obj = Fernet(key)
    return obj.encrypt(data)


def fernet_decrypt(cipher: bytes, key: bytes) -> bytes:
    """
    decrypt ciphers with the fernet cryptosystem

    :param cipher: the cipher
    :param key: the key
    :return: the plaintext
    """
    try:
        from cryptography.fernet import Fernet
    except (ImportError, ModuleNotFoundError):
        from subprocess import check_call
        from sys import executable
        check_call([executable, '-m', 'pip', 'install', 'cryptography'])
        from cryptography.fernet import Fernet
    obj = Fernet(key)
    return obj.decrypt(cipher)


def rsa_fernet_encrypt(data: bytes, e: int, n: int, oe: int, od: int, on: int) -> bytes:
    """
    encrypt data using a mix of fernet encryption and the rsa cryptosystem (recommended asymmetric method)
    protects against several kinds of attacks and supports signatures

    :param data: the plaintext
    :param e: public key (e) of the other person
    :param n: public key (n) of the other person
    :param oe: your public key (e)
    :param od: your private key
    :param on: your public key (n)
    :return: the ciphertext
    """
    from base64 import urlsafe_b64encode, urlsafe_b64decode
    try:
        from mmath import bytes_to_int, int_to_bytes
        from mhash import sha256
    except (ImportError, ModuleNotFoundError):
        from mmL.mmath import bytes_to_int, int_to_bytes
        from mmL.mhash import sha256
    key = generate_fernet_key()
    cipher = fernet_encrypt(data, key)
    enc_key = urlsafe_b64encode(int_to_bytes(rsa_encrypt(bytes_to_int(urlsafe_b64decode(key)), e, n)))
    signature = urlsafe_b64encode(int_to_bytes(rsa_encrypt(bytes_to_int(sha256(data)), od, on)))
    r = b'\x01.' + enc_key + b'.' + cipher + b'.' + signature + b'.' + \
        urlsafe_b64encode(int_to_bytes(oe)) + b'.' + urlsafe_b64encode(int_to_bytes(on))
    return r


def rsa_fernet_decrypt(cipher: bytes, d: int, n: int, disable_checksum: bool = False) -> bytes:
    """
    decrypt data using a mix of fernet encryption and the rsa cryptosystem

    :param cipher: the ciphertext
    :param d: your private key
    :param n:your public key (n)
    :param disable_checksum: disable signature checks (NOT recommended)
    :return: the plaintext
    """
    from base64 import urlsafe_b64encode, urlsafe_b64decode
    try:
        from mmath import bytes_to_int, int_to_bytes
        from mhash import sha256
    except (ImportError, ModuleNotFoundError):
        from mmL.mmath import bytes_to_int, int_to_bytes
        from mmL.mhash import sha256
    c = cipher.split(b'.')
    if len(c) != 6:
        raise ValueError('cipher is corrupted')
    if c[0] != b'\x01':
        raise ValueError('This cipher version is not supported')
    key = urlsafe_b64encode(int_to_bytes(rsa_decrypt(bytes_to_int(urlsafe_b64decode(c[1])), d, n)))
    data = fernet_decrypt(c[2], key)
    if disable_checksum:
        return data
    hashed = sha256(data)
    oe = bytes_to_int(urlsafe_b64decode(c[4]))
    on = bytes_to_int(urlsafe_b64decode(c[5]))
    signature = int_to_bytes(rsa_decrypt(bytes_to_int(urlsafe_b64decode(c[3])), oe, on))
    if signature != hashed:
        raise ValueError('Signature is invalid')
    return data


def rsa_fernet_signature(cipher: bytes, d: int, n: int) -> [bool, int, int, int]:
    """
    get information about a cipher

    :param cipher: the ciphertext
    :param d: your private key
    :param n: your public key (n)
    :return: [has valid signature; public key (e) of sender; public key (n) of sender; version]
    """
    from base64 import urlsafe_b64encode, urlsafe_b64decode
    try:
        from mmath import bytes_to_int, int_to_bytes
        from mhash import sha256
    except (ImportError, ModuleNotFoundError):
        from mmL.mmath import bytes_to_int, int_to_bytes
        from mmL.mhash import sha256
    c = cipher.split(b'.')
    if len(c) != 6:
        raise ValueError('cipher is corrupted')
    if c[0] != b'\x01':
        raise ValueError('This cipher version is not supported')
    key = urlsafe_b64encode(int_to_bytes(rsa_decrypt(bytes_to_int(urlsafe_b64decode(c[1])), d, n)))
    data = fernet_decrypt(c[2], key)
    hashed = sha256(data)
    oe = bytes_to_int(urlsafe_b64decode(c[4]))
    on = bytes_to_int(urlsafe_b64decode(c[5]))
    signature = int_to_bytes(rsa_decrypt(bytes_to_int(urlsafe_b64decode(c[3])), oe, on))
    if signature == hashed:
        return [True, oe, on, bytes_to_int(c[0])]
    else:
        return [False, oe, on, bytes_to_int(c[0])]

