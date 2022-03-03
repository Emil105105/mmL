

def miller_prime(n: int, iterations: int = 48) -> bool:
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
    return int(n)


def ceil(n: float) -> int:
    if n.is_integer():
        return int(n)
    else:
        return int(n + 1.0)


def gcd(a, b):
    if b == 0:
        return a
    return gcd(b, a % b)


def lcm(a, b):
    return a * b // gcd(a, b)


def bytes_to_int(n: bytes):
    r = 0
    for p in n:
        r *= 256
        r += p
    return r


def int_to_bytes(n: int):
    r = b''
    x = n
    while x > 0:
        r = bytes([x % 256]) + r
        x //= 256
    return r


def float_to_ratio(n: float) -> (int, int):
    x = str(n).split('.')
    y = len(x[1])
    a = int(x[0]) * pow(10, y) + int(x[1])
    b = pow(10, y)
    z = gcd(a, b)
    return a // z, b // z


def next_prime(n: int, max_guess: int = 65536, allow_same: bool = False) -> int:
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


def sqrt(n: int) -> float:
    return n ** 0.5


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(sqrt(n)) + 2, 2):
        if n % i == 0:
            return False
    return True

class Q:

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

    def add_ratio(self, a, b) -> None:
        x = lcm(self.denominator, b)
        self.numerator *= x // self.denominator
        self.denominator = x
        self.numerator += a * x
        self._reduce()

    def subtract_ratio(self, a, b) -> None:
        x = lcm(self.denominator, b)
        self.numerator *= x // self.denominator
        self.denominator = x
        self.numerator -= a * x
        self._reduce()

    def multiply_ratio(self, a, b):
        self.numerator *= a
        self.denominator *= b
        self._reduce()

    def divide_ratio(self, a, b):
        self.numerator *= b
        self.denominator *= a
        self._reduce()