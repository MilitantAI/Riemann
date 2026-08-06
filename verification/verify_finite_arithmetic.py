"""Exact finite checks for the arithmetic and scalar-residual ledgers."""

from fractions import Fraction
from itertools import product


COVERED_LABELS = {
    "prop:finite-ancestry-laws",
    "prop:truncated-algebra-restriction",
    "prop:finite-moebius-inverse",
    "prop:finite-euler-inversion",
    "prop:exact-scalarisation-boundary",
    "prop:boundary-residual-transport",
    "prop:finite-additive-multiplicative-ledger",
    "prop:ordinary-euler-product-ledger",
    "prop:euler-cutoff-transport",
}

CHECKS = 0


def check(condition: bool, message: str) -> None:
    global CHECKS
    CHECKS += 1
    if not condition:
        raise AssertionError(message)


def primes_up_to(limit: int) -> list[int]:
    primes: list[int] = []
    for candidate in range(2, limit + 1):
        if all(candidate % p for p in primes if p * p <= candidate):
            primes.append(candidate)
    return primes


def factor(n: int) -> dict[int, int]:
    result: dict[int, int] = {}
    remainder = n
    for p in primes_up_to(n):
        if p * p > remainder:
            break
        while remainder % p == 0:
            result[p] = result.get(p, 0) + 1
            remainder //= p
    if remainder > 1:
        result[remainder] = result.get(remainder, 0) + 1
    return result


def largest_prime_factor(n: int) -> int:
    return max(factor(n), default=1)


def mobius(n: int) -> int:
    ancestry = factor(n)
    if any(exponent > 1 for exponent in ancestry.values()):
        return 0
    return -1 if len(ancestry) % 2 else 1


def divisors(n: int) -> list[int]:
    return [d for d in range(1, n + 1) if n % d == 0]


def convolution(f: list[Fraction], g: list[Fraction], n_max: int) -> list[Fraction]:
    result = [Fraction(0) for _ in range(n_max + 1)]
    for n in range(1, n_max + 1):
        result[n] = sum((f[d] * g[n // d] for d in divisors(n)), Fraction(0))
    return result


def scalar(f: list[Fraction], start: int, stop: int, s: int) -> Fraction:
    return sum((f[n] / n**s for n in range(start, stop + 1)), Fraction(0))


def boundary(f: list[Fraction], g: list[Fraction], n_max: int, s: int) -> Fraction:
    return sum(
        (
            f[a] * g[b] / (a * b) ** s
            for a in range(1, n_max + 1)
            for b in range(1, n_max + 1)
            if a * b > n_max
        ),
        Fraction(0),
    )


def smooth(n: int, y: int) -> bool:
    return largest_prime_factor(n) <= y


def exponent_box_products(n_max: int, y: int) -> list[int]:
    powers: list[list[int]] = []
    for p in primes_up_to(min(n_max, y)):
        entries = [1]
        value = p
        while value <= n_max:
            entries.append(value)
            value *= p
        powers.append(entries)
    if not powers:
        return [1]
    return [value for choices in product(*powers) for value in [prod(choices)]]


def prod(values: tuple[int, ...] | list[int]) -> int:
    result = 1
    for value in values:
        result *= value
    return result


def run() -> None:
    # Unique-factorisation coordinates add under multiplication.
    for a in range(1, 41):
        for b in range(1, 41):
            expected = factor(a)
            for p, exponent in factor(b).items():
                expected[p] = expected.get(p, 0) + exponent
            check(factor(a * b) == expected, f"ancestry failed for {a}*{b}")

    # Restriction-compatible Möbius inversion.
    for n_max in range(1, 61):
        ones = [Fraction(0)] + [Fraction(1) for _ in range(n_max)]
        mu = [Fraction(0)] + [Fraction(mobius(n)) for n in range(1, n_max + 1)]
        epsilon = [Fraction(0) for _ in range(n_max + 1)]
        epsilon[1] = Fraction(1)
        check(convolution(ones, mu, n_max) == epsilon, f"Mobius inverse at N={n_max}")

    for n_max in range(2, 31):
        f = [Fraction(0)] + [Fraction((3 * n + 1) % 7 - 3) for n in range(1, n_max + 1)]
        g = [Fraction(0)] + [Fraction((5 * n + 2) % 11 - 5) for n in range(1, n_max + 1)]
        conv_n = convolution(f, g, n_max)
        for m in (1, n_max // 2, n_max - 1):
            check(
                conv_n[: m + 1] == convolution(f[: m + 1], g[: m + 1], m),
                f"restriction homomorphism at M={m}, N={n_max}",
            )

    # Finite Euler elements, scalar boundary, and boundary transport.
    for n_max in range(1, 36):
        for y in (1, 2, 3, 5, 11, 37):
            euler = [Fraction(0)] + [
                Fraction(int(smooth(n, y))) for n in range(1, n_max + 1)
            ]
            inverse = [Fraction(0)] + [
                Fraction(mobius(n) if smooth(n, y) else 0)
                for n in range(1, n_max + 1)
            ]
            epsilon = [Fraction(0) for _ in range(n_max + 1)]
            epsilon[1] = Fraction(1)
            check(
                convolution(euler, inverse, n_max) == epsilon,
                f"finite Euler inverse at N={n_max}, y={y}",
            )

            for s in (0, 1, 2):
                left = scalar(convolution(euler, inverse, n_max), 1, n_max, s)
                right = (
                    scalar(euler, 1, n_max, s)
                    * scalar(inverse, 1, n_max, s)
                    - boundary(euler, inverse, n_max, s)
                )
                check(left == right, f"scalar boundary at N={n_max}, y={y}, s={s}")

    for n_max in range(3, 31):
        f = [Fraction(0)] + [Fraction((n % 5) - 2) for n in range(1, n_max + 1)]
        g = [Fraction(0)] + [Fraction((2 * n % 7) - 3) for n in range(1, n_max + 1)]
        conv_n = convolution(f, g, n_max)
        for m in (1, n_max // 2, n_max - 1):
            for s in (0, 1, 2):
                b_m = boundary(f[: m + 1], g[: m + 1], m, s)
                f_head = scalar(f, 1, m, s)
                g_head = scalar(g, 1, m, s)
                f_tail = scalar(f, m + 1, n_max, s)
                g_tail = scalar(g, m + 1, n_max, s)
                conv_tail = scalar(conv_n, m + 1, n_max, s)
                transported = b_m + f_head * g_tail + g_head * f_tail
                transported += f_tail * g_tail - conv_tail
                check(
                    boundary(f, g, n_max, s) == transported,
                    f"boundary transport at M={m}, N={n_max}, s={s}",
                )

    # Finite additive--multiplicative and ordinary Euler ledgers.
    for n_max in range(1, 31):
        for y in (1, 2, 3, 5, 7, 13, 31):
            box = exponent_box_products(n_max, y)
            for s in (0, 1, 2):
                q_product = sum((Fraction(1, value**s) for value in box), Fraction(0))
                overshoot = sum(
                    (Fraction(1, value**s) for value in box if value > n_max),
                    Fraction(0),
                )
                unresolved = sum(
                    (
                        Fraction(1, n**s)
                        for n in range(1, n_max + 1)
                        if not smooth(n, y)
                    ),
                    Fraction(0),
                )
                z_n = sum((Fraction(1, n**s) for n in range(1, n_max + 1)), Fraction(0))
                check(
                    z_n == q_product - overshoot + unresolved,
                    f"finite Euler ledger at N={n_max}, y={y}, s={s}",
                )

            pi_y = prod(
                [Fraction(p * p, p * p - 1) for p in primes_up_to(y)]
            )
            resolved = sum(
                (
                    Fraction(1, n * n)
                    for n in range(1, n_max + 1)
                    if smooth(n, y)
                ),
                Fraction(0),
            )
            ordinary_overshoot = pi_y - resolved
            unresolved = sum(
                (
                    Fraction(1, n * n)
                    for n in range(1, n_max + 1)
                    if not smooth(n, y)
                ),
                Fraction(0),
            )
            z_n = sum((Fraction(1, n * n) for n in range(1, n_max + 1)), Fraction(0))
            check(
                z_n == pi_y - ordinary_overshoot + unresolved,
                f"ordinary Euler ledger at N={n_max}, y={y}",
            )

    # Integer and prime cutoff transport.
    for n_max in range(1, 30):
        for y in (1, 2, 3, 5, 11):
            for s in (0, 1, 2):
                a_n = sum(
                    (
                        Fraction(1, n**s)
                        for n in range(1, n_max + 1)
                        if smooth(n, y)
                    ),
                    Fraction(0),
                )
                a_next = sum(
                    (
                        Fraction(1, n**s)
                        for n in range(1, n_max + 2)
                        if smooth(n, y)
                    ),
                    Fraction(0),
                )
                increment = Fraction(int(smooth(n_max + 1, y)), (n_max + 1) ** s)
                check(a_next == a_n + increment, "integer cutoff transport")
                u_n = sum(
                    (
                        Fraction(1, n**s)
                        for n in range(1, n_max + 1)
                        if not smooth(n, y)
                    ),
                    Fraction(0),
                )
                u_next = sum(
                    (
                        Fraction(1, n**s)
                        for n in range(1, n_max + 2)
                        if not smooth(n, y)
                    ),
                    Fraction(0),
                )
                unresolved_increment = Fraction(
                    int(not smooth(n_max + 1, y)), (n_max + 1) ** s
                )
                check(
                    u_next == u_n + unresolved_increment,
                    "unresolved integer cutoff transport",
                )
                if s > 0:
                    pi_y = prod(
                        [
                            Fraction(p**s, p**s - 1)
                            for p in primes_up_to(y)
                        ]
                    )
                    o_n = pi_y - a_n
                    o_next = pi_y - a_next
                    check(
                        o_next == o_n - increment,
                        "overshoot integer cutoff transport",
                    )

        for y, z in ((1, 3), (2, 5), (3, 11)):
            delta = sum(
                (
                    Fraction(1, n * n)
                    for n in range(1, n_max + 1)
                    if y < largest_prime_factor(n) <= z
                ),
                Fraction(0),
            )
            a_y = sum(
                (
                    Fraction(1, n * n)
                    for n in range(1, n_max + 1)
                    if smooth(n, y)
                ),
                Fraction(0),
            )
            a_z = sum(
                (
                    Fraction(1, n * n)
                    for n in range(1, n_max + 1)
                    if smooth(n, z)
                ),
                Fraction(0),
            )
            check(a_z == a_y + delta, "prime cutoff transport")
            u_y = sum(
                (
                    Fraction(1, n * n)
                    for n in range(1, n_max + 1)
                    if not smooth(n, y)
                ),
                Fraction(0),
            )
            u_z = sum(
                (
                    Fraction(1, n * n)
                    for n in range(1, n_max + 1)
                    if not smooth(n, z)
                ),
                Fraction(0),
            )
            check(u_z == u_y - delta, "unresolved prime cutoff transport")
            pi_y = prod(
                [Fraction(p * p, p * p - 1) for p in primes_up_to(y)]
            )
            pi_z = prod(
                [Fraction(p * p, p * p - 1) for p in primes_up_to(z)]
            )
            o_y = pi_y - a_y
            o_z = pi_z - a_z
            check(
                o_z == o_y + pi_z - pi_y - delta,
                "overshoot prime cutoff transport",
            )

    print(f"finite arithmetic: {CHECKS} exact checks passed")


if __name__ == "__main__":
    run()
