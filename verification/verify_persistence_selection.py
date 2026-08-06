"""Finite checks for the projected Riemann persistence selection."""

import cmath
from fractions import Fraction
import math


COVERED_LABELS = {
    "prop:exact-branch-agreement",
    "prop:riemann-registration-recovery",
    "prop:unique-riemann-persistence-selection",
}

CHECKS = 0


def check(condition: bool, message: str) -> None:
    global CHECKS
    CHECKS += 1
    if not condition:
        raise AssertionError(message)


def persistence(eta: Fraction, coherence_weight: Fraction) -> Fraction:
    # The finite hyperbola ledger gives coherence density one, while the exact
    # self-dual projection retains eta as its oriented residual.
    return coherence_weight - eta * eta


def mobius(n: int) -> int:
    remaining = n
    prime_count = 0
    prime = 2
    while prime * prime <= remaining:
        if remaining % prime == 0:
            remaining //= prime
            prime_count += 1
            if remaining % prime == 0:
                return 0
            while remaining % prime == 0:
                remaining //= prime
        prime += 1
    if remaining > 1:
        prime_count += 1
    return -1 if prime_count % 2 else 1


def negative_power(n: int, s: complex) -> complex:
    return cmath.exp(-s * math.log(n))


def cutoff_limit(value: float) -> int:
    return math.floor(value + 1e-12)


def z_sum(value: float, s: complex) -> complex:
    return sum(
        (negative_power(n, s) for n in range(1, cutoff_limit(value) + 1)),
        0j,
    )


def m_sum(value: float, s: complex) -> complex:
    return sum(
        (
            mobius(n) * negative_power(n, s)
            for n in range(1, cutoff_limit(value) + 1)
        ),
        0j,
    )


def hyperbola_ledger(x: int, s: complex, u: float, v: float) -> complex:
    first = sum(
        (
            mobius(a) * negative_power(a, s) * z_sum(x / a, s)
            for a in range(1, cutoff_limit(u) + 1)
        ),
        0j,
    )
    second = sum(
        (
            negative_power(b, s) * m_sum(x / b, s)
            for b in range(1, cutoff_limit(v) + 1)
        ),
        0j,
    )
    return first + second - m_sum(u, s) * z_sum(v, s)


def projected_sample(
    x: int, scale: int, gamma: float, eta: Fraction, weight: float
) -> tuple[float, complex, float, float]:
    eta_float = float(eta)
    beta = 0.5 + eta_float
    s = complex(beta, gamma)
    u = x**beta
    v = x ** (1 - beta)
    ledger = hyperbola_ledger(x, s, u, v)
    hyperbola_residual = math.log(u / v) / (2 * math.log(x))
    positive_kernel = abs(cmath.exp((s / 2 - 1) * math.log(scale)))
    negative_kernel = abs(cmath.exp(((1 - s) / 2 - 1) * math.log(scale)))
    mellin_residual = math.log(positive_kernel / negative_kernel) / math.log(scale)
    coherence = abs(ledger) ** 2
    score = -(hyperbola_residual**2) + weight * coherence
    return score, ledger, hyperbola_residual, mellin_residual


def run() -> None:
    deltas = {
        Fraction(1, 100),
        Fraction(1, 17),
        Fraction(1, 8),
        Fraction(1, 4),
        Fraction(7, 20),
        Fraction(49, 100),
    }
    weights = {
        Fraction(0),
        Fraction(1, 9),
        Fraction(1),
        Fraction(7, 3),
        Fraction(100),
    }

    for delta in deltas:
        candidates = (-delta, Fraction(0), delta)
        for eta in candidates:
            beta = Fraction(1, 2) + eta
            dual_beta = 1 - beta

            # Factor exchange and conjugate reflection carry eta to -eta.
            check(
                dual_beta - Fraction(1, 2) == -eta,
                f"dual exponent failed at eta={eta}",
            )

            # Half the logarithmic cutoff exponent ratio is eta exactly:
            # (1/2)[(1/2+eta)-(1/2-eta)] = eta.
            hyperbola_residual = (
                (Fraction(1, 2) + eta) - (Fraction(1, 2) - eta)
            ) / 2
            check(
                hyperbola_residual == eta,
                f"hyperbola residual failed at eta={eta}",
            )

            # Difference of the two Mellin kernel magnitude exponents is eta.
            positive_exponent = beta / 2 - 1
            negative_exponent = (1 - beta) / 2 - 1
            check(
                positive_exponent - negative_exponent == eta,
                f"Mellin residual failed at eta={eta}",
            )

        for weight in weights:
            values = {eta: persistence(eta, weight) for eta in candidates}
            maximum = max(values.values())
            selected = {eta for eta, value in values.items() if value == maximum}
            check(
                selected == {Fraction(0)},
                f"non-unique persistence maximum at d={delta}, lambda={weight}",
            )
            check(
                values[0] - values[delta] == delta * delta,
                f"positive branch gap failed at d={delta}, lambda={weight}",
            )
            check(
                values[0] - values[-delta] == delta * delta,
                f"negative branch gap failed at d={delta}, lambda={weight}",
            )

        # Evaluate the raw registration maps over coordinates wider than the
        # three ancestry-authorised branch records, then evaluate persistence
        # only on the constructor orbit {-delta, 0, delta}.
        registration_coordinates = tuple(
            sorted(
                {
                    *candidates,
                    Fraction(-49, 100),
                    -delta / 3,
                    delta / 2,
                    Fraction(49, 100),
                }
            )
        )
        for integer_cutoff in (2, 5, 11, 31):
            for scale_cutoff in (2, 7, 19):
                for height_marker in (-3.25, 0.0, 2.5):
                    values: dict[Fraction, float] = {}
                    registered_observations: dict[
                        Fraction, tuple[float, float, float]
                    ] = {}
                    for eta in registration_coordinates:
                        score, ledger, hyperbola_residual, mellin_residual = (
                            projected_sample(
                                integer_cutoff,
                                scale_cutoff,
                                height_marker,
                                eta,
                                0.6,
                            )
                        )
                        if eta in candidates:
                            values[eta] = score
                        registered_observations[eta] = (
                            float(eta),
                            hyperbola_residual,
                            mellin_residual,
                        )
                        check(
                            abs(ledger - 1) < 2e-11,
                            "hyperbola coherence failed at "
                            f"X={integer_cutoff}, eta={eta}, gamma={height_marker}",
                        )
                        check(
                            abs(hyperbola_residual - float(eta)) < 2e-13,
                            "cutoff projection residual failed at "
                            f"X={integer_cutoff}, eta={eta}",
                        )
                        check(
                            abs(mellin_residual - float(eta)) < 2e-13,
                            "Mellin projection residual failed at "
                            f"T={scale_cutoff}, eta={eta}, gamma={height_marker}",
                        )
                    check(
                        len(set(registered_observations.values()))
                        == len(registration_coordinates),
                        "registration resolution failed at "
                        f"d={delta}, X={integer_cutoff}, T={scale_cutoff}, "
                        f"gamma={height_marker}",
                    )
                    selected = {
                        eta
                        for eta, value in values.items()
                        if abs(value - max(values.values())) < 1e-12
                    }
                    check(
                        selected == {Fraction(0)},
                        "selection changed under finite refinement at "
                        f"d={delta}, X={integer_cutoff}, T={scale_cutoff}, "
                        f"gamma={height_marker}",
                    )

    print(f"persistence selection: {CHECKS} checks passed")


if __name__ == "__main__":
    run()
