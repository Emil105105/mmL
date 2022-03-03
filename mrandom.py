

def rand_bytes(number_of_bytes: int) -> bytes:
    from os import urandom
    return urandom(number_of_bytes)


def rand_ratio(accuracy: int = 16, include_one: bool = False, disable_gcd: bool = False) -> (int, int):
    if accuracy < 1:
        raise ValueError('Accuracy cannot be lower than 1')
    try:
        from mmath import gcd, bytes_to_int
    except (ImportError, ModuleNotFoundError):
        from mmL.mmath import gcd, bytes_to_int
    x = bytes_to_int(rand_bytes(accuracy))
    if include_one:
        y = pow(256, accuracy) - 1
    else:
        y = pow(256, accuracy)
    if not disable_gcd:
        z = gcd(x, y)
        x //= z
        y //= z
    return x, y


def rand() -> float:
    x, y = rand_ratio(disable_gcd=True)
    return x / y


def rand_below_ratio(a: int, b: int = 1, disable_gcd: bool = False) -> (int, int):
    if b == 0:
        raise ZeroDivisionError('[ It is impossible to divide by zero. If you could, you could proof that 1 = 2:\n'
                                'a = b\na² = ab\na²-b² = ab-b²\n(a+b)(a-b) = b(a-b)\na+b = b\n2b = b\n2 = 1 ]')
    try:
        from mmath import gcd
    except (ImportError, ModuleNotFoundError):
        from mmL.mmath import gcd
    n = 4
    c = a // b
    while c > 1:
        c //= 256
        n += 1
    x, y = rand_ratio(n, False, disable_gcd)
    x *= a
    y *= b
    if not disable_gcd:
        z = gcd(x, y)
        x //= z
        y //= z
    return x, y


def rand_below_int(n: int) -> int:
    x, y = rand_below_ratio(n, 1, True)
    return x // y


def randint(a: int, b: int) -> int:
    return rand_below_int(b - a) + a


def randint_except(a: int, b: int, e: list, max_guess: int = 65536) -> int:
    for j in range(max_guess):
        x = randint(a, b - len(e))
        for i in e:
            if i <= x:
                x += 1
        if x < b and x not in e:
            return x
    raise InterruptedError('Maximum guesses reached')


def rand_bits(number_of_bits: int) -> str:
    return bin(randint(pow(2, number_of_bits - 1), pow(2, number_of_bits)))[2:]


def random_prime(bits: int, max_guesses: int = 65536) -> int:
    if bits < 2:
        raise ValueError('There is no prime number')
    try:
        from mmath import miller_prime
    except (ImportError, ModuleNotFoundError):
        from mmL.mmath import miller_prime
    for i in range(max_guesses):
        x = int(rand_bits(bits), 2)
        if miller_prime(x):
            return x
    raise InterruptedError('Maximum guesses reached')
