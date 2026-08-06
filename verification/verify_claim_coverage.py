"""Audit labelled mathematical claims against executable or manual validation."""

import ast
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "riemann_cogenetic_whitepaper.tex"

COMPUTATIONAL = {
    "prop:finite-ancestry-laws": "verify_finite_arithmetic.py",
    "prop:truncated-algebra-restriction": "verify_finite_arithmetic.py",
    "prop:finite-moebius-inverse": "verify_finite_arithmetic.py",
    "prop:finite-euler-inversion": "verify_finite_arithmetic.py",
    "prop:exact-scalarisation-boundary": "verify_finite_arithmetic.py",
    "prop:boundary-residual-transport": "verify_finite_arithmetic.py",
    "prop:finite-additive-multiplicative-ledger": "verify_finite_arithmetic.py",
    "prop:ordinary-euler-product-ledger": "verify_finite_arithmetic.py",
    "prop:euler-cutoff-transport": "verify_finite_arithmetic.py",
    "prop:finite-continuation-cocycle": "verify_continuation_transport.py",
    "prop:theta-residual-transport": "verify_continuation_transport.py",
    "prop:finite-gaussian-poisson-bridge": "verify_continuation_transport.py",
    "prop:mellin-functional-symmetry": "verify_continuation_transport.py",
    "prop:finite-moebius-hyperbola": "verify_hyperbola_invariant.py",
    "prop:arbitrary-hyperbola-cutoff": "verify_hyperbola_invariant.py",
    "cor:exact-hyperbola-transport": "verify_hyperbola_invariant.py",
    "prop:unique-self-dual-cutoff": "verify_hyperbola_invariant.py",
    "prop:inverse-convolution-universality": "verify_hyperbola_invariant.py",
    "prop:finite-mobius-mellin-ledger": "verify_hyperbola_invariant.py",
    "prop:exact-branch-agreement": "verify_persistence_selection.py",
    "prop:riemann-registration-recovery": "verify_persistence_selection.py",
    "prop:unique-riemann-persistence-selection": "verify_persistence_selection.py",
}

MANUAL = {
    "prop:fixed-locus": "elementary complex arithmetic",
    "prop:symmetry-not-fixedness": "direct functional-equation consequence",
    "prop:continuation-projection": "uniform Bernoulli-tail bound",
    "thm:mobius-growth-obstruction": "holomorphic-continuation contradiction",
    "cor:off-line-zero-implies-persistence": "growth obstruction plus reflection",
    "prop:zeta-carrier-ancestry": "dependency audit",
    "lem:riemann-tail-stability": "finite-prefix invariance of a limsup obstruction",
    "prop:riemann-differential-typing": "declared Cogenesis grammar",
    "prop:riemann-selection-refinement": (
        "dependency audit across arithmetic, continuation, theta, and transform transports"
    ),
    "prop:riemann-no-orphan-closure": "dependency and normalisation audit",
    "prop:off-line-candidate-status": "complete-record status distinction",
    "thm:critical-line-closure": (
        "explicit causal completion through the typed normalisation record"
    ),
    "thm:riemann-hypothesis": "critical-line closure plus fixed-locus arithmetic",
}

REQUIRED_FOUNDATIONAL_LABELS = {
    "rev:foundational-inference",
    "eq:foundational-inference",
    "eq:required-local-implication",
}


def declared_labels(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if any(
            isinstance(target, ast.Name) and target.id == "COVERED_LABELS"
            for target in node.targets
        ):
            value = ast.literal_eval(node.value)
            return set(value)
    raise AssertionError(f"{path.name} does not declare COVERED_LABELS")


def run() -> None:
    source = MANUSCRIPT.read_text(encoding="utf-8")
    labelled_claims = set(
        re.findall(
            r"\\begin\{(?:theorem|proposition|corollary|lemma)\}"
            r".*?\\label\{([^}]+)\}",
            source,
            flags=re.DOTALL,
        )
    )
    covered = set(COMPUTATIONAL) | set(MANUAL)

    missing = sorted(labelled_claims - covered)
    stale = sorted(covered - labelled_claims)
    if missing:
        raise AssertionError(f"unmapped labelled claims: {missing}")
    if stale:
        raise AssertionError(f"coverage entries without claims: {stale}")

    expected_by_verifier: dict[str, set[str]] = {}
    for label, verifier in COMPUTATIONAL.items():
        expected_by_verifier.setdefault(verifier, set()).add(label)

    for verifier, expected_labels in expected_by_verifier.items():
        path = Path(__file__).with_name(verifier)
        if not path.is_file():
            raise AssertionError(f"missing verifier {verifier}")
        declared = declared_labels(path)
        if declared != expected_labels:
            missing_labels = sorted(expected_labels - declared)
            stale_labels = sorted(declared - expected_labels)
            raise AssertionError(
                f"{verifier} coverage mismatch: "
                f"missing={missing_labels}, stale={stale_labels}"
            )

    for label in REQUIRED_FOUNDATIONAL_LABELS:
        if f"\\label{{{label}}}" not in source:
            raise AssertionError(f"missing isolated foundational label: {label}")

    forbidden = ("load" + "-bearing")
    if forbidden in source.lower():
        raise AssertionError("superseded terminology remains in manuscript")

    print(
        "claim coverage: "
        f"{len(labelled_claims)} labelled claims mapped "
        f"({len(COMPUTATIONAL)} executable, {len(MANUAL)} manual/causal)"
    )


if __name__ == "__main__":
    run()
