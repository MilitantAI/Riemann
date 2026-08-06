# A Cogenetic Proof of the Riemann Hypothesis

Morgan Petrik (Militant.AI)  
Version 1.0 — 6 August 2026  
DOI: [10.5281/zenodo.21817670](https://doi.org/10.5281/zenodo.21817670)

This repository contains the manuscript, LaTeX source, bibliography, and
executable supporting material for *A Cogenetic Proof of the Riemann
Hypothesis*.

## Proof structure

The paper derives the zero-forming process from finite arithmetic ancestry
rather than treating zero, completed infinity, or functional symmetry as
causal primitives. Its principal stages are:

1. finite Dirichlet-convolution and Möbius ancestry;
2. exact continuation, theta, Poisson, and Mellin residual transport;
3. the finite Möbius–hyperbola invariant and its unique self-dual resolution;
4. the exponent differential forced by a hypothetical off-line zero;
5. registration-derived context, resolution, and admissible branch records;
6. finite persistence selection with every unselected record retained;
7. ancestry-first causal completion of the zero projection; and
8. recovery of the classical critical-line statement.

The foundational causal extension is isolated in the manuscript rather than
hidden inside analytic machinery.

## Repository contents

- `riemann_cogenetic_whitepaper.pdf` — compiled Version 1.0 paper.
- `riemann_cogenetic_whitepaper.tex` — complete LaTeX source.
- `references.bib` — bibliography.
- `verification/` — standard-library Python verification suite.
- `CITATION.cff` — machine-readable GitHub citation metadata.
- `.zenodo.json` — machine-readable Zenodo deposit metadata.

## Verification

Requirements:

- Python 3.10 or later;
- no third-party Python packages.

Run the complete suite from the repository root:

```shell
python verification/run_all.py
```

The Version 1.0 suite performs **18,377 checks** across **35 labelled claims**:
22 executable claims and 13 explicit analytic or causal-process obligations.
Each verifier exits non-zero on failure.

The scripts verify finite identities, widened coefficient families, residual
transport, persistence ordering, and claim coverage. They accompany the proof;
they do not replace its analytic derivations.

## Building the paper

Requirements:

- TeX Live 2024 or an equivalent LaTeX distribution;
- `latexmk`, `pdflatex`, and `biber`.

Build from the repository root:

```shell
latexmk -pdf -interaction=nonstopmode -halt-on-error riemann_cogenetic_whitepaper.tex
```

Generated LaTeX intermediates are excluded by `.gitignore`.

## Methodological sources

- *Cogenesis: A Process-First Formalism for Reality*  
  [10.5281/zenodo.20539999](https://doi.org/10.5281/zenodo.20539999)
- *Cogenesis: Causal Singularity of Now*  
  [10.5281/zenodo.21804643](https://doi.org/10.5281/zenodo.21804643)
- *A Cogenetic Proof of the Collatz Relation*  
  [10.5281/zenodo.21802635](https://doi.org/10.5281/zenodo.21802635)

## Citation

```bibtex
@misc{petrik2026riemann,
  author    = {Petrik, Morgan},
  title     = {A Cogenetic Proof of the Riemann Hypothesis},
  year      = {2026},
  version   = {1.0},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.21817670},
  url       = {https://doi.org/10.5281/zenodo.21817670}
}
```

