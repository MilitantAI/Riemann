"""Run every Riemann manuscript verifier and propagate any failure."""

from pathlib import Path
import subprocess
import sys


SCRIPTS = (
    "verify_finite_arithmetic.py",
    "verify_continuation_transport.py",
    "verify_hyperbola_invariant.py",
    "verify_persistence_selection.py",
    "verify_claim_coverage.py",
)


def run() -> None:
    directory = Path(__file__).resolve().parent
    for script in SCRIPTS:
        print(f"==> {script}", flush=True)
        subprocess.run(
            [sys.executable, str(directory / script)],
            cwd=directory.parent,
            check=True,
        )
    print(f"all verification clusters passed ({len(SCRIPTS)} scripts)")


if __name__ == "__main__":
    run()
