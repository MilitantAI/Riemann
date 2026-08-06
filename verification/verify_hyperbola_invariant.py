"""Exact checks for the Möbius--hyperbola and Möbius--Mellin claims."""

import cmath
from fractions import Fraction
import math


COVERED_LABELS = {
    "prop:finite-moebius-hyperbola",
    "prop:arbitrary-hyperbola-cutoff",
    "cor:exact-hyperbola-transport",
    "prop:unique-self-dual-cutoff",
    "prop:inverse-convolution-universality",
    "prop:finite-mobius-mellin-ledger",
}

CHECKS = 0


def check(condition: bool, message: str) -> None:
    global CHECKS
    CHECKS += 1
    if not condition:
        raise AssertionError(message)


def divisors(n: int) -> list[int]:
    return [d for d in range(1, n + 1) if n % d == 0]


def mobius(n: int) -> int:
    remaining = n
    prime_count = 0
    p = 2
    while p * p <= remaining:
        if remaining % p == 0:
            remaining //= p
            prime_count += 1
            if remaining % p == 0:
                return 0
            while remaining % p == 0:
                remaining //= p
        p += 1
    if remaining > 1:
        prime_count += 1
    return -1 if prime_count % 2 else 1


def z_sum(y: Fraction, s: int) -> Fraction:
    return sum(
        (Fraction(1, n**s) for n in range(1, y.numerator // y.denominator + 1)),
        Fraction(0),
    )


def m_sum(y: Fraction, s: int) -> Fraction:
    return sum(
        (
            Fraction(mobius(n), n**s)
            for n in range(1, y.numerator // y.denominator + 1)
        ),
        Fraction(0),
    )


def hyperbola_invariant(x: int, s: int) -> Fraction:
    return sum(
        (
            Fraction(mobius(a), (a * b) ** s)
            for a in range(1, x + 1)
            for b in range(1, x // a + 1)
        ),
        Fraction(0),
    )


def hyperbola_ledger(x: int, u: Fraction, s: int) -> Fraction:
    v = Fraction(x, 1) / u
    a_term = sum(
        (
            Fraction(mobius(a), a**s) * z_sum(Fraction(x, a), s)
            for a in range(1, u.numerator // u.denominator + 1)
        ),
        Fraction(0),
    )
    b_term = sum(
        (
            Fraction(1, b**s) * m_sum(Fraction(x, b), s)
            for b in range(1, v.numerator // v.denominator + 1)
        ),
        Fraction(0),
    )
    return a_term + b_term - m_sum(u, s) * z_sum(v, s)


def convolution(f: list[Fraction], g: list[Fraction], n: int) -> Fraction:
    return sum((f[d] * g[n // d] for d in divisors(n)), Fraction(0))


def dirichlet_inverse(f: list[Fraction]) -> list[Fraction]:
    n_max = len(f) - 1
    g = [Fraction(0) for _ in range(n_max + 1)]
    g[1] = Fraction(1, 1) / f[1]
    for n in range(2, n_max + 1):
        subtotal = sum(
            (f[d] * g[n // d] for d in divisors(n) if d > 1),
            Fraction(0),
        )
        g[n] = -subtotal / f[1]
    return g


def run() -> None:
    # The invariant and arbitrary real cutoff ledger.
    for x in range(1, 81):
        cutoffs = {
            Fraction(1),
            Fraction(x),
            Fraction(2, 3),
            Fraction(3, 2),
            Fraction(5, 4),
            Fraction(2 * x, 3),
        }
        for s in (0, 1, 2, 3):
            check(hyperbola_invariant(x, s) == 1, f"I_X at X={x}, s={s}")
            ledger_values = []
            for u in cutoffs:
                value = hyperbola_ledger(x, u, s)
                ledger_values.append(value)
                check(value == 1, f"hyperbola split at X={x}, u={u}, s={s}")
            check(
                all(value == ledger_values[0] for value in ledger_values),
                f"cutoff transport at X={x}, s={s}",
            )

    # Widen from (1, mu) to deterministic finite inverse-convolution families.
    for n_max in range(1, 51):
        families = (
            [Fraction(0)] + [Fraction(1 if n == 1 else (n % 5) - 2) for n in range(1, n_max + 1)],
            [Fraction(0)] + [Fraction(2 if n == 1 else (3 * n % 7) - 3) for n in range(1, n_max + 1)],
            [Fraction(0)] + [Fraction(-1 if n == 1 else (5 * n % 11) - 5) for n in range(1, n_max + 1)],
        )
        for family_number, f in enumerate(families, start=1):
            g = dirichlet_inverse(f)
            for n in range(1, n_max + 1):
                expected = Fraction(1 if n == 1 else 0)
                check(
                    convolution(f, g, n) == expected,
                    f"inverse family {family_number}, n={n}, N={n_max}",
                )
            for s in (0, 1, 2):
                invariant = sum(
                    (convolution(f, g, n) / n**s for n in range(1, n_max + 1)),
                    Fraction(0),
                )
                check(
                    invariant == 1,
                    f"widened invariant family {family_number}, N={n_max}, s={s}",
                )

    # Exact finite Abel/Mellin ledger in the untwisted channel.
    for x in range(1, 81):
        mertens = [sum(mobius(n) for n in range(1, k + 1)) for k in range(x + 1)]
        for z in (1, 2, 3, 4):
            left = sum(
                (Fraction(mobius(n), n**z) for n in range(1, x + 1)),
                Fraction(0),
            )
            integral = sum(
                (
                    Fraction(mertens[k], 1)
                    * (Fraction(1, k**z) - Fraction(1, (k + 1) ** z))
                    / z
                    for k in range(1, x)
                ),
                Fraction(0),
            )
            right = Fraction(mertens[x], x**z) + z * integral
            check(left == right, f"Abel ledger at X={x}, z={z}")

    # Twisted finite Abel/Mellin ledger, including phase and complex exponent.
    for x in range(1, 51):
        for gamma in (-3.25, -0.5, 0.75, 4.0):
            twisted_mertens = [
                sum(
                    (
                        mobius(n) * cmath.exp(-1j * gamma * math.log(n))
                        for n in range(1, k + 1)
                    ),
                    0j,
                )
                for k in range(x + 1)
            ]
            for z in (1.4 + 0.3j, 2.2 - 0.8j, 3.0 + 1.1j):
                left = sum(
                    (
                        mobius(n)
                        * cmath.exp(-(z + 1j * gamma) * math.log(n))
                        for n in range(1, x + 1)
                    ),
                    0j,
                )
                integral = sum(
                    (
                        twisted_mertens[k]
                        * (
                            cmath.exp(-z * math.log(k))
                            - cmath.exp(-z * math.log(k + 1))
                        )
                        / z
                        for k in range(1, x)
                    ),
                    0j,
                )
                boundary = twisted_mertens[x] * cmath.exp(-z * math.log(x))
                check(
                    abs(left - (boundary + z * integral)) < 2e-12,
                    f"twisted Abel ledger at X={x}, gamma={gamma}, z={z}",
                )

    # The continuous fixed exponent is the unique rational solution of 2 theta=1.
    candidates = [Fraction(n, 24) for n in range(-24, 49)]
    fixed = [theta for theta in candidates if theta == 1 - theta]
    check(fixed == [Fraction(1, 2)], "unique self-dual exponent")

    print(f"hyperbola invariant: {CHECKS} exact checks passed")


if __name__ == "__main__":
    run()
