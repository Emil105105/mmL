

def rand_bytes(number_of_bytes: int) -> bytes:
    """
    generate random bytes

    :param number_of_bytes: the number of bytes
    :return: the bytes
    """
    from os import urandom
    return urandom(number_of_bytes)


def rand_fraction(accuracy: int = 16, include_one: bool = False, disable_gcd: bool = False) -> (int, int):
    """
    generate a random fraction between 0 and 1

    :param accuracy: the 256th log of the denominator
    :param include_one: include the number one
    :param disable_gcd: reduce resource usage
    :return: a fraction (numerator, denominator)
    """
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
    """
    generate a random number between 0 and 1

    :return: a float between 0 and 1 (not including 1)
    """
    x, y = rand_fraction(disable_gcd=True)
    return x / y


def rand_below_fraction(a: int, b: int = 1, disable_gcd: bool = False) -> (int, int):
    """
    generate a random fraction between 0 and the input

    :param a: numerator
    :param b: denominator
    :param disable_gcd: reduce resource usage
    :return: a random fraction between 0 and a/b
    """
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
    x, y = rand_fraction(n, False, disable_gcd)
    x *= a
    y *= b
    if not disable_gcd:
        z = gcd(x, y)
        x //= z
        y //= z
    return x, y


def rand_below_int(n: int) -> int:
    """
    generate a random integer between 0 and the input

    :param n: any integer
    :return: a random number between 0 and n
    """
    x, y = rand_below_fraction(n, 1, True)
    return x // y


def randint(a: int, b: int) -> int:
    """
    generate a random integer between two integers

    :param a: lower limit
    :param b: upper limit (NOT included)
    :return: a random integer between a and b
    """
    return rand_below_int(b - a) + a


def randint_except(a: int, b: int, e: list, max_guess: int = 65536) -> int:
    """
    generate a random integer between two integers which isn't included in a list

    :param a: lower limit
    :param b: upper limit (NOT included)
    :param e: list of exceptions
    :param max_guess: maximum number of guesses
    :return: a random integer between a and b which isn't in e
    """
    for j in range(max_guess):
        x = randint(a, b - len(e))
        for i in e:
            if i <= x:
                x += 1
        if x < b and x not in e:
            return x
    raise InterruptedError('Maximum guesses reached')


def rand_bits(number_of_bits: int) -> str:
    """
    generate a random sequence of bits

    :param number_of_bits: number of bits (length)
    :return: a random sequence of bits
    """
    try:
        from mmath import bytes_to_int
    except (ImportError, ModuleNotFoundError):
        from mmL.mmath import bytes_to_int
    x = rand_bytes(number_of_bits // 8 + 1)
    y = bytes_to_int(x)
    z = y % pow(2, number_of_bits)
    return format(z, '0' + str(number_of_bits) + 'b')


def random_prime(bits: int, max_guesses: int = 65536) -> int:
    """
    generate a random prime with a specified number of bits

    :param bits: number of bits (length)
    :param max_guesses: maximum number of guesses before an error occurs
    :return: a random prime with a specified number of bits
    """
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
