"""Exact and high-precision checks for continuation and scale transport."""

from cmath import exp as cexp
from fractions import Fraction
from math import comb, factorial, log, pi


COVERED_LABELS = {
    "prop:finite-continuation-cocycle",
    "prop:theta-residual-transport",
    "prop:finite-gaussian-poisson-bridge",
    "prop:mellin-functional-symmetry",
}

CHECKS = 0
BERNOULLI = {
    0: Fraction(1),
    1: Fraction(-1, 2),
    2: Fraction(1, 6),
    3: Fraction(0),
    4: Fraction(-1, 30),
    5: Fraction(0),
    6: Fraction(1, 42),
}


def check(condition: bool, message: str) -> None:
    global CHECKS
    CHECKS += 1
    if not condition:
        raise AssertionError(message)


def pochhammer(s: int, length: int) -> int:
    result = 1
    for j in range(length):
        result *= s + j
    return result


def bernoulli_polynomial_coefficients(degree: int) -> list[Fraction]:
    return [
        Fraction(comb(degree, j)) * BERNOULLI[degree - j]
        for j in range(degree + 1)
    ]


def periodic_bernoulli_power_integral(
    degree: int, power: int, start: int, stop: int
) -> Fraction:
    """Integrate B_degree({x}) x**power over integer endpoints exactly."""
    coefficients = bernoulli_polynomial_coefficients(degree)
    result = Fraction(0)
    for k in range(start, stop):
        for j, coefficient in enumerate(coefficients):
            for ell in range(power + 1):
                result += (
                    coefficient
                    * comb(power, ell)
                    * k ** (power - ell)
                    / Fraction(j + ell + 1)
                )
    return result


def continuation_residual(s: int, m: int, start: int, stop: int) -> Fraction:
    power = -s - 2 * m
    if power < 0:
        raise ValueError("exact verifier requires polynomial residual integrand")
    integral = periodic_bernoulli_power_integral(2 * m, power, start, stop)
    return -Fraction(pochhammer(s, 2 * m), factorial(2 * m)) * integral


def z_sum(n_max: int, s: int) -> Fraction:
    if s <= 0:
        return sum((Fraction(n ** (-s)) for n in range(1, n_max + 1)), Fraction(0))
    return sum((Fraction(1, n**s) for n in range(1, n_max + 1)), Fraction(0))


def power(base: int, exponent: int) -> Fraction:
    if exponent >= 0:
        return Fraction(base**exponent)
    return Fraction(1, base ** (-exponent))


def continuation_coordinate(s: int, m: int, n_max: int) -> Fraction:
    value = z_sum(n_max, s)
    value += power(n_max, 1 - s) / (s - 1)
    value -= power(n_max, -s) / 2
    for r in range(1, m + 1):
        value += (
            BERNOULLI[2 * r]
            * pochhammer(s, 2 * r - 1)
            * power(n_max, 1 - s - 2 * r)
            / factorial(2 * r)
        )
    return value


def theta(n_max: int, x: float) -> float:
    return sum(
        (cexp(-pi * n * n * x).real for n in range(-n_max, n_max + 1)),
        0.0,
    )


def theta_defect(n_max: int, m_max: int, x: float) -> float:
    return theta(n_max, x) - x ** (-0.5) * theta(m_max, 1 / x)


def simpson(function, start: float, stop: float, panels: int = 4096):
    if panels % 2:
        panels += 1
    width = (stop - start) / panels
    total = function(start) + function(stop)
    total += 4 * sum(function(start + j * width) for j in range(1, panels, 2))
    total += 2 * sum(function(start + j * width) for j in range(2, panels, 2))
    return total * width / 3


def finite_fourier_coefficient(k: int, x: float, length: int) -> complex:
    return simpson(
        lambda value: cexp(-pi * x * value * value - 2j * pi * k * value),
        -length - 0.5,
        length + 0.5,
    )


def psi(n_max: int, x: float) -> float:
    return (theta(n_max, x) - 1) / 2


def finite_mellin_coordinate(n_max: int, scale: float, s: complex) -> complex:
    polar = 1 / (s - 1) - 1 / s
    integral = simpson(
        lambda x: psi(n_max, x)
        * (
            cexp((s / 2 - 1) * log(x))
            + cexp(((1 - s) / 2 - 1) * log(x))
        ),
        1,
        scale,
        panels=2048,
    )
    return polar + integral


def run() -> None:
    # Exact Euler--Maclaurin residual signs and cocycle.
    cases = ((-3, 1), (-4, 1), (-5, 2), (-6, 2), (-7, 3))
    for s, m in cases:
        for start in range(1, 8):
            for stop in range(start + 1, 13):
                residual = continuation_residual(s, m, start, stop)
                transport = continuation_coordinate(s, m, stop)
                transport -= continuation_coordinate(s, m, start)
                check(
                    transport == residual,
                    f"continuation transport s={s}, m={m}, {start}->{stop}",
                )

                middle = (start + stop) // 2
                if start < middle < stop:
                    composed = continuation_residual(s, m, start, middle)
                    composed += continuation_residual(s, m, middle, stop)
                    check(
                        residual == composed,
                        f"continuation cocycle s={s}, m={m}, {start}->{stop}",
                    )

    # Exact theta defect involution and refinement transport.
    for x in (0.4, 0.75, 1.0, 1.7, 3.0):
        for n_max, m_max in ((0, 0), (1, 2), (3, 5), (7, 4)):
            defect = theta_defect(n_max, m_max, x)
            dual = -x ** (-0.5) * theta_defect(m_max, n_max, 1 / x)
            check(abs(defect - dual) < 2e-13, "theta defect involution")

            refined = theta_defect(n_max + 2, m_max + 3, x) - defect
            explicit = 2 * sum(
                cexp(-pi * n * n * x).real
                for n in range(n_max + 1, n_max + 3)
            )
            explicit -= 2 * x ** (-0.5) * sum(
                cexp(-pi * k * k / x).real
                for k in range(m_max + 1, m_max + 4)
            )
            check(abs(refined - explicit) < 2e-13, "theta refinement transport")

    # The finite Gaussian--Poisson bridge, with both finite residual types present.
    for x in (0.7, 1.0, 1.8):
        for length, frequency in ((1, 1), (2, 2), (3, 2)):
            coefficients = {
                k: finite_fourier_coefficient(k, x, length)
                for k in range(-frequency, frequency + 1)
            }
            p_zero = theta(length, x)
            fourier_residual = p_zero - sum(coefficients.values())
            bridge = fourier_residual + sum(
                coefficients[k] - x ** (-0.5) * cexp(-pi * k * k / x)
                for k in coefficients
            )
            defect = theta_defect(length, frequency, x)
            check(abs(bridge - defect) < 5e-12, "finite Gaussian--Poisson bridge")

    # Exact lower-to-upper Mellin transport retains the finite theta defect.
    for n_max, m_max in ((1, 2), (3, 1), (5, 4)):
        for scale in (1.5, 2.5, 4.0):
            for s in (0.3 + 0.7j, -1.2 + 1.1j, 2.4 - 0.6j):
                left = simpson(
                    lambda x: psi(n_max, x)
                    * cexp((s / 2 - 1) * log(x)),
                    1 / scale,
                    1,
                    panels=2048,
                )
                dual = simpson(
                    lambda x: psi(m_max, x)
                    * cexp(((1 - s) / 2 - 1) * log(x)),
                    1,
                    scale,
                    panels=2048,
                )
                elementary = (
                    (1 - cexp(((1 - s) / 2) * log(scale))) / (s - 1)
                    - (1 - cexp((-s / 2) * log(scale))) / s
                )
                residual = 0.5 * simpson(
                    lambda x: theta_defect(n_max, m_max, x)
                    * cexp((s / 2 - 1) * log(x)),
                    1 / scale,
                    1,
                    panels=2048,
                )
                check(
                    abs(left - dual - elementary - residual) < 2e-10,
                    "finite Mellin scale transport",
                )

    # Symmetry exists at finite Mellin resolution, before static projection.
    for n_max in (1, 3, 6):
        for scale in (1.5, 2.5, 4.0):
            for s in (0.3 + 0.7j, -1.2 + 1.1j, 2.4 - 0.6j):
                left = finite_mellin_coordinate(n_max, scale, s)
                right = finite_mellin_coordinate(n_max, scale, 1 - s)
                check(abs(left - right) < 2e-11, "finite Mellin symmetry")

    # The theta modular defect contracts under balanced sequential refinement.
    for x in (0.5, 0.8, 1.0, 1.4, 2.0):
        check(abs(theta_defect(12, 12, x)) < 2e-12, "theta sequential projection")

    print(f"continuation transport: {CHECKS} checks passed")


if __name__ == "__main__":
    run()
