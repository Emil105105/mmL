

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
    key = int_to_bytes(rsa_decrypt(bytes_to_int(urlsafe_b64decode(c[1])), d, n))
    while len(key) < 32:
        key = b'\x00' + key
    data = fernet_decrypt(c[2], urlsafe_b64encode(key))
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
    key = int_to_bytes(rsa_decrypt(bytes_to_int(urlsafe_b64decode(c[1])), d, n))
    while len(key) < 32:
        key = b'\x00' + key
    data = fernet_decrypt(c[2], urlsafe_b64encode(key))
    hashed = sha256(data)
    oe = bytes_to_int(urlsafe_b64decode(c[4]))
    on = bytes_to_int(urlsafe_b64decode(c[5]))
    signature = int_to_bytes(rsa_decrypt(bytes_to_int(urlsafe_b64decode(c[3])), oe, on))
    if signature == hashed:
        return [True, oe, on, bytes_to_int(c[0])]
    else:
        return [False, oe, on, bytes_to_int(c[0])]


def generate_symmetric_key(key_size: int = 16) -> bytes:
    """
    generate a random key for symmetric encryption

    :param key_size: size in bytes
    :return: a random key
    """
    try:
        from mrandom import rand_bytes
    except (ImportError, ModuleNotFoundError):
        from mmL.mrandom import rand_bytes
    return rand_bytes(key_size)


def symmetric_encrypt(data: bytes, key: bytes, block_size: int = 4) -> bytes:
    """
    symmetrically encrypt data using a custom algorithm (which is not proven to be secure)

    :param data: the data
    :param key: any key
    :param block_size: square root of the size of blocks
    :return: a cipher text
    """
    try:
        from mmath import bytes_xor, int_to_bytes
        from mhash import any_hash
    except (ImportError, ModuleNotFoundError):
        from mmL.mmath import bytes_xor, int_to_bytes
        from mmL.mhash import any_hash
    box = [99, 124, 119, 123, 242, 107, 111, 197, 48, 1, 103, 43, 254, 215, 171, 118, 202, 130, 201, 125, 250, 89, 71, 
           240, 173, 212, 162, 175, 156, 164, 114, 192, 183, 253, 147, 38, 54, 63, 247, 204, 52, 165, 229, 241, 113, 
           216, 49, 21, 4, 199, 35, 195, 24, 150, 5, 154, 7, 18, 128, 226, 235, 39, 178, 117, 9, 131, 44, 26, 27, 110, 
           90, 160, 82, 59, 214, 179, 41, 227, 47, 132, 83, 209, 0, 237, 32, 252, 177, 91, 106, 203, 190, 57, 74, 76,
           88, 207, 208, 239, 170, 251, 67, 77, 51, 133, 69, 249, 2, 127, 80, 60, 159, 168, 81, 163, 64, 143, 146, 157,
           56, 245, 188, 182, 218, 33, 16, 255, 243, 210, 205, 12, 19, 236, 95, 151, 68, 23, 196, 167, 126, 61, 100, 93, 
           25, 115, 96, 129, 79, 220, 34, 42, 144, 136, 70, 238, 184, 20, 222, 94, 11, 219, 224, 50, 58, 10, 73, 6, 36,
           92, 194, 211, 172, 98, 145, 149, 228, 121, 231, 200, 55, 109, 141, 213, 78, 169, 108, 86, 244, 234, 101, 122, 
           174, 8, 186, 120, 37, 46, 28, 166, 180, 198, 232, 221, 116, 31, 75, 189, 139, 138, 112, 62, 181, 102, 72, 3, 
           246, 14, 97, 53, 87, 185, 134, 193, 29, 158, 225, 248, 152, 17, 105, 217, 142, 148, 155, 30, 135, 233, 206, 
           85, 40, 223, 140, 161, 137, 13, 191, 230, 66, 104, 65, 153, 45, 15, 176, 84, 187, 22]
    if block_size <= 1 or block_size >= 256 or len(data) >= 2 ** (2 ** 8):
        raise ValueError()
    size = len(data).to_bytes(8, 'big')
    block = block_size ** 2
    data = size + data
    while len(data) % block != 0:
        data += generate_symmetric_key(1)
    blocks = [data[i:i + block] for i in range(0, len(data), block)]
    key = b'\xc2\xed\x83\xd7' + key + b'\xde\xb2\xae\xbb'
    first_key = any_hash(key, block, 17)
    last_key = any_hash(bytes_xor(any_hash(b'\x12\xb0\xa6\x0b' + key, block, 3), first_key), block, 7)
    keys = []
    for i in range(len(blocks)):
        last_key = any_hash(bytes_xor(last_key, first_key) + int_to_bytes(i ** 2 + 1), block, 7)
        keys.append(last_key)
    cipher = int_to_bytes(block_size)
    for i in range(len(blocks)):
        b = [0 for _ in range(block)]
        for j in range(block):
            b[(j * (block_size + 1) + ((block_size + 5) * 7 + 11)) % block] = blocks[i][j]
        a = []
        for j in keys[i]:
            a.append(j)
        c = []
        for j in range(block):
            c.append(a[j] ^ box[b[j]])
        cipher += bytes(c)
    return cipher


def symmetric_decrypt(cipher: bytes, key: bytes) -> bytes:
    """
    decrypt symmetric ciphers

    :param cipher: the cipher text
    :param key: the key
    :return: the data
    """
    try:
        from mmath import bytes_xor, int_to_bytes, bytes_to_int
        from mhash import any_hash
    except (ImportError, ModuleNotFoundError):
        from mmL.mmath import bytes_xor, int_to_bytes, bytes_to_int
        from mmL.mhash import any_hash
    i_box = [82, 9, 106, 213, 48, 54, 165, 56, 191, 64, 163, 158, 129, 243, 215, 251, 124, 227, 57, 130, 155, 47, 255,
             135, 52, 142, 67, 68, 196, 222, 233, 203, 84, 123, 148, 50, 166, 194, 35, 61, 238, 76, 149, 11, 66, 250,
             195, 78, 8, 46, 161, 102, 40, 217, 36, 178, 118, 91, 162, 73, 109, 139, 209, 37, 114, 248, 246, 100, 134,
             104, 152, 22, 212, 164, 92, 204, 93, 101, 182, 146, 108, 112, 72, 80, 253, 237, 185, 218, 94, 21, 70, 87,
             167, 141, 157, 132, 144, 216, 171, 0, 140, 188, 211, 10, 247, 228, 88, 5, 184, 179, 69, 6, 208, 44, 30,
             143, 202, 63, 15, 2, 193, 175, 189, 3, 1, 19, 138, 107, 58, 145, 17, 65, 79, 103, 220, 234, 151, 242, 207,
             206, 240, 180, 230, 115, 150, 172, 116, 34, 231, 173, 53, 133, 226, 249, 55, 232, 28, 117, 223, 110, 71,
             241, 26, 113, 29, 41, 197, 137, 111, 183, 98, 14, 170, 24, 190, 27, 252, 86, 62, 75, 198, 210, 121, 32,
             154, 219, 192, 254, 120, 205, 90, 244, 31, 221, 168, 51, 136, 7, 199, 49, 177, 18, 16, 89, 39, 128, 236,
             95, 96, 81, 127, 169, 25, 181, 74, 13, 45, 229, 122, 159, 147, 201, 156, 239, 160, 224, 59, 77, 174, 42,
             245, 176, 200, 235, 187, 60, 131, 83, 153, 97, 23, 43, 4, 126, 186, 119, 214, 38, 225, 105, 20, 99, 85, 33,
             12, 125]
    block_size = cipher[0]
    block = block_size ** 2
    cipher = cipher[1:]
    blocks = [cipher[i:i + block] for i in range(0, len(cipher), block)]
    key = b'\xc2\xed\x83\xd7' + key + b'\xde\xb2\xae\xbb'
    first_key = any_hash(key, block, 17)
    last_key = any_hash(bytes_xor(any_hash(b'\x12\xb0\xa6\x0b' + key, block, 3), first_key), block, 7)
    keys = []
    for i in range(len(blocks)):
        last_key = any_hash(bytes_xor(last_key, first_key) + int_to_bytes(i ** 2 + 1), block, 7)
        keys.append(last_key)
    data = b''
    for i in range(len(blocks)):
        a = []
        for j in keys[i]:
            a.append(j)
        b = []
        for j in range(block):
            b.append(i_box[a[j] ^ blocks[i][j]])
        c = []
        for j in range(block):
            c.append((j * (block_size + 1) + ((block_size + 5) * 7 + 11)) % block)
        d = [0 for _ in range(block)]
        for j in range(block):
            d[c.index(j)] = b[j]
        data += bytes(d)
    size = bytes_to_int(data[0:8])
    data = data[8:][:size]
    return data


def rsa_extended_encrypt(data: bytes, e: int, n: int, oe: int, od: int, on: int) -> bytes:
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
    key = urlsafe_b64encode(generate_symmetric_key(32))
    cipher = urlsafe_b64encode(symmetric_encrypt(data, key, 8))
    enc_key = urlsafe_b64encode(int_to_bytes(rsa_encrypt(bytes_to_int(urlsafe_b64decode(key)), e, n)))
    signature = urlsafe_b64encode(int_to_bytes(rsa_encrypt(bytes_to_int(sha256(data)), od, on)))
    r = b'\x02.' + enc_key + b'.' + cipher + b'.' + signature + b'.' + \
        urlsafe_b64encode(int_to_bytes(oe)) + b'.' + urlsafe_b64encode(int_to_bytes(on))
    return r


def rsa_extended_decrypt(cipher: bytes, d: int, n: int, disable_checksum: bool = False) -> bytes:
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
    if c[0] != b'\x02':
        raise ValueError('This cipher version is not supported')
    key = urlsafe_b64encode(int_to_bytes(rsa_decrypt(bytes_to_int(urlsafe_b64decode(c[1])), d, n)))
    while len(key) < 32:
        key = b'\x00' + key
    data = symmetric_decrypt(urlsafe_b64decode(c[2]), key)
    if disable_checksum:
        return data
    hashed = sha256(data)
    oe = bytes_to_int(urlsafe_b64decode(c[4]))
    on = bytes_to_int(urlsafe_b64decode(c[5]))
    signature = int_to_bytes(rsa_decrypt(bytes_to_int(urlsafe_b64decode(c[3])), oe, on))
    if signature != hashed:
        raise ValueError('Signature is invalid')
    return data


def rsa_extended_signature(cipher: bytes, d: int, n: int) -> [bool, int, int, int]:
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
    if c[0] != b'\x02':
        raise ValueError('This cipher version is not supported')
    key = urlsafe_b64encode(int_to_bytes(rsa_decrypt(bytes_to_int(urlsafe_b64decode(c[1])), d, n)))
    while len(key) < 32:
        key = b'\x00' + key
    data = symmetric_decrypt(urlsafe_b64decode(c[2]), key)
    hashed = sha256(data)
    oe = bytes_to_int(urlsafe_b64decode(c[4]))
    on = bytes_to_int(urlsafe_b64decode(c[5]))
    signature = int_to_bytes(rsa_decrypt(bytes_to_int(urlsafe_b64decode(c[3])), oe, on))
    if signature == hashed:
        return [True, oe, on, bytes_to_int(c[0])]
    else:
        return [False, oe, on, bytes_to_int(c[0])]
