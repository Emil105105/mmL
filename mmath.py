

def miller_prime(n: int, iterations: int = 48) -> bool:
    """
    check if a number is prime using the miller method (may incorrectly indentify numbers as prime)

    :param n: the number
    :param iterations: higher values -> higher accuracy -> more resource usage;
                       lower values -> lower accuracy -> less resource usage
    :return: True (is a prime) or False (is NOT a prime)
    """
    try:
        from mrandom import randint
    except (ImportError, ModuleNotFoundError):
        from mmL.mrandom import randint
    if n < 2:
        return False
    if n in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
        return True
    for i in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
        if n % i == 0:
            return False
    r = 0
    s = n - 1
    while s % 2 == 0:
        r += 1
        s //= 2
    for i in range(iterations):
        a = randint(2, n - 1)
        x = pow(a, s, n)
        if x == 1 or x == n - 1:
            continue
        for j in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def floor(n: float) -> int:
    """
    calculate the largest integer <= n

    :param n: any number
    :return: the largest integer <= n
    """
    return int(n)


def ceil(n: float) -> int:
    """
    calculate the smallest integer >= n

    :param n: any number
    :return: the smallest integer >= n
    """
    if n.is_integer():
        return int(n)
    else:
        return int(n + 1.0)


def gcd(a: int, b: int) -> int:
    """
    calculate the greatest common divisor of a and b

    :param a: any integer
    :param b: any integer
    :return: the greatest common divisor
    """
    if b == 0:
        return a
    return gcd(b, a % b)


def lcm(a: int, b: int) -> int:
    """
    calculate the least common multiple of a and b

    :param a: any integer
    :param b: any integer
    :return: the least common multiple
    """
    return a * b // gcd(a, b)


def bytes_xor(a: bytes, b: bytes, short: bool = False) -> bytes:
    if short:
        return bytes(x ^ y for x, y in zip(a, b))
    elif len(a) != len(b):
        raise ValueError('both bytes objects must have the same length')
    else:
        return bytes(x ^ y for x, y in zip(a, b))


def bytes_to_int(n: bytes) -> int:
    """
    turn bytes into an integer

    :param n: the bytes
    :return: the integer
    """
    r = 0
    for p in n:
        r *= 256
        r += p
    return r


def int_to_bytes(n: int) -> bytes:
    """
    turn an integer into bytes

    :param n: the integer
    :return: the bytes
    """
    r = b''
    x = n
    while x > 0:
        r = bytes([x % 256]) + r
        x //= 256
    return r


def float_to_fraction(n: float, use_brute_force: bool = True, disable_gcd: bool = False, max_iterations: int = 16777215) -> (int, int):
    """
    turn a number into a fraction (numerator, denominator)

    :param n: any number
    :param use_brute_force: get expected result for rational numbers
    :param disable_gcd: save resources, doesn't affect brute force method
    :param max_iterations: maximum guesses using brute force
    :return: the fraction (numerator, denominator)
    """
    if use_brute_force:
        if n == 1/1:
            return 1, 1
        elif n == 0/1:
            return 0, 1
        else:
            x = 1
            y = 1
            z = 0
            for _ in range(max_iterations):
                if y == 1 and z == 3:
                    z = 0
                    x += 1
                elif z == 0:
                    z = 1
                    y += 1
                elif x == 1 and z == 1:
                    z = 2
                    y += 1
                elif z == 2:
                    z = 3
                    x += 1
                elif z == 1:
                    y += 1
                    x -= 1
                elif z == 3:
                    y -= 1
                    x += 1
                else:
                    raise Exception()
                if n == x / y:
                    return x, y
            print(x, y)
            c = str(n).split('.')
            y = len(c[1])
            a = int(c[0]) * pow(10, y) + int(c[1])
            b = pow(10, y)
            z = gcd(a, b)
            a //= z
            b //= z
            return a, b
    else:
        c = str(n).split('.')
        y = len(c[1])
        a = int(c[0]) * pow(10, y) + int(c[1])
        b = pow(10, y)
    if not disable_gcd:
        z = gcd(a, b)
        a //= z
        b //= z
    return a, b


def next_prime(n: int, max_guess: int = 65536, allow_same: bool = False) -> int:
    """
    calculate the next prime number

    :param n: any integer
    :param max_guess: the number of maximum guesses before an error
    :param allow_same: return n if n is a prime
    :return: the next prime
    """
    if allow_same:
        if miller_prime(n):
            return n
    if n < 2:
        return 2
    if n % 2 == 0:
        n += 1
    else:
        n += 2
    for i in range(0, max_guess, 2):
        if miller_prime(n + i):
            return n + i
    raise InterruptedError('Maximum guesses reached')


def sqrt(n: float, depth: int = None) -> float:
    """
    calculate an approximation to the square root of any number

    :param n: any number
    :param depth: higher values -> higher accuracy -> more resource usage;
                  lower values -> lower accuracy -> less resource usage
                  None = automatic
    :return: the square root
    """
    a = 1.0
    b = n
    if depth is None:
        while True:
            a = (a + b) / 2
            b = n / a
            if abs(a - b) < 0.000244140625:
                return b
    for i in range(depth):
        a = (a + b) / 2
        b = n / a
    return b


def sqrt_q(x, y, depth: int = None) -> (int, int):
    """
    calculate an approximation to the square root of a fraction

    :param x: numerator
    :param y: denominator
    :param depth: higher values -> higher accuracy -> more resource usage;
                  lower values -> lower accuracy -> less resource usage
                  None = automatic
    :return: the square root (numerator, denominator)
    """
    a, b = 1, 1
    c, d = x, y
    if depth is None:
        while True:
            a = a * d + c * b
            b = b * d * 2
            c = b * x
            d = a * y
            if abs(a / b - c / d) < 0.000244140625:
                z = gcd(c, d)
                return c // z, d // z
    for i in range(depth):
        a = a * d + c * b
        b = b * d * 2
        c = b * x
        d = a * y
    z = gcd(c, d)
    return c // z, d // z


def sqrt_n(n: int) -> int:
    """
    get the square root (or the biggest integer smaller than it) of any integer

    :param n: any integer
    :return:
    """
    if n == 0:
        return 0
    if n == 1:
        return 1
    for i in range(n):
        if pow(i, 2) > n:
            return i - 1


def is_prime(n: int) -> bool:
    """
    check if an integer is a prime

    :param n: any integer
    :return: True (is a prime) or False (is NOT a prime)
    """
    if n < 2:
        return False
    if n in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, sqrt_n(n) + 2, 2):
        if n % i == 0 and i < n:
            return False
    return True


class Q:
    """
    A class for fractions
    """

    def __init__(self, n=None) -> None:
        if n is None:
            self.numerator = 0
            self.denominator = 1
        elif isinstance(n, float):
            x = str(n).split('.')
            y = len(x[1])
            self.numerator = int(x[0]) * pow(10, y) + int(x[1])
            self.denominator = pow(10, y)
            self._reduce()
        elif isinstance(n, int):
            self.numerator = n
            self.denominator = 1
            self._reduce()
        else:
            raise TypeError(str(type(n)) + ' is not supported')

    def get(self) -> (int, int):
        return self.numerator, self.denominator

    def get_int(self) -> int:
        return self.numerator // self.denominator

    def get_float(self) -> float:
        return self.numerator / self.denominator

    def _reduce(self) -> None:
        x = gcd(self.denominator, self.numerator)
        self.denominator //= x
        self.numerator //= x

    def set_int(self, n: int) -> None:
        self.numerator = n
        self.denominator = 1
        self._reduce()

    def set_float(self, n: float) -> None:
        x = str(n).split('.')
        y = len(x[1])
        self.numerator = int(x[0]) * pow(10, y) + int(x[1])
        self.denominator = pow(10, y)
        self._reduce()

    def set(self, numerator: int, denominator: int = 1) -> None:
        if denominator == 0:
            raise ZeroDivisionError('[ It is impossible to divide by zero. If you could, you could proof that 1 = 2:\n'
                                    'a = b\na² = ab\na²-b² = ab-b²\n(a+b)(a-b) = b(a-b)\na+b = b\n2b = b\n2 = 1 ]')
        else:
            self.numerator = numerator
            self.denominator = denominator
            self._reduce()

    def add(self, n: int) -> None:
        self.numerator += n * self.denominator
        self._reduce()

    def subtract(self, n: int) -> None:
        self.numerator -= n * self.denominator
        self._reduce()

    def multiply(self, n: int) -> None:
        self.numerator *= n
        self._reduce()

    def divide(self, n: int) -> None:
        self.denominator *= n
        self._reduce()

    def add_fraction(self, a, b) -> None:
        x = lcm(self.denominator, b)
        self.numerator *= x // self.denominator
        self.denominator = x
        self.numerator += a * x
        self._reduce()

    def subtract_fraction(self, a, b) -> None:
        x = lcm(self.denominator, b)
        self.numerator *= x // self.denominator
        self.denominator = x
        self.numerator -= a * x
        self._reduce()

    def multiply_fraction(self, a, b):
        self.numerator *= a
        self.denominator *= b
        self._reduce()

    def divide_fraction(self, a, b):
        self.numerator *= b
        self.denominator *= a
        self._reduce()
