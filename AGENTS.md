# Riemann — project context

## What this is

An attempt to apply the Cogenesis framework to the Riemann hypothesis, following the
Collatz paper that preceded it. Morgan Petrik (Militant.AI) is the author; the agent's
job is derivation, verification, and honest adversarial reading, not encouragement.

Respond in Australian English.

## The precedent

The Collatz work lives at [MilitantAI/Collatz](https://github.com/MilitantAI/Collatz),
DOI `10.5281/zenodo.21802635`. Read the manuscript before contributing here — the
method matters more than the result.

Foundational sources, both by the same author:

- Cogenesis: A Process-First Formalism for Reality — DOI `10.5281/zenodo.20539999`
- Cogenesis: Causal Singularity of Now (concise) — DOI `10.5281/zenodo.21804643`,
  concept DOI `10.5281/zenodo.21770073`

## The foundational axiom

Cogenesis declares, in advance of any application, that infinity denotes unbounded
sequential continuation, never a completed totality or attained object. A limit at
infinity is indefinitely continued refinement, not approach to an infinite endpoint.
No causal enactment performs infinitely many steps as a completed operation and then
returns a set one can traverse all at once.

This is the axiom that carries the Collatz argument. Its single load-bearing inference
— from a property of the relation to a property of every orbit — is an application of
that convention together with carrier exhaustion. The paper isolates that step
explicitly rather than burying it, states its scope exactly, and tells the reader to
direct objections there and nowhere else.

Expect the Riemann argument to rest on the same move, and hold it to the same standard:
name the step, isolate it, and do not let it hide inside machinery.

## Why Riemann specifically

The Collatz paper states its own criterion for when the load-bearing step earns
credence: recurrence. One instance is an expression of the argument, not evidence for
it. Evidence would be a second problem whose resistance has the same shape — one whose
statement quantifies over a completed process at a resolution at which the process does
not close.

So this project is not a victory lap. It is the test the previous paper set for itself.
If the same move does not do real work here, that is a finding about the framework and
should be reported as one.

## How the Collatz work was actually done

These are the practices that produced a defensible result. They are not style
preferences.

**Derive, don't import.** The block map, anchor ladder, generator, and sign law were
derived from the Collatz relation itself. Classical machinery was brought in only to
locate the existing literature against the result, never to carry it. Riemann has a far
deeper classical apparatus than Collatz, so the temptation to import is correspondingly
larger. Prior work — the author's own included — should be read as evidence of
direction, not adopted as scaffold.

**No approximations.** Every link in the cycle-bound chain is an exact identity in
integer or rational arithmetic. When a bound was reached by estimate, it was rederived
exactly. If a step needs an inequality that only holds approximately, that is a defect
to fix, not a detail to note.

**Verify every claim in code.** Each section's propositions are checked by scripts that
exit non-zero on failure — 111 checks over the Collatz manuscript, standard library
only. Coverage was audited by mapping the paper's theorem labels against what the
scripts actually test, and the gaps were closed rather than excused.

**Widen statements so tests can falsify them.** Claims stated only for the target case
often cannot be tested at all: `3n+1` supplies a single cycle and therefore cannot test
an inequality about cycles. Restating the results for `3n+d` over odd `d` made 87 cycles
available and turned untestable assertions into falsifiable ones. Look for the analogous
widening here.

**Say what changed and why.** When editing the manuscript, produce a manifest of the
changes with the reasoning for each, and keep a revert path. Do not make silent
adjustments, and never adjust a statement so that it happens to fit a known answer.

**Distinguish the two orders.** Cogenesis supplies discovery and relational
contextualisation; exact arithmetic supplies validation. Neither replaces the other,
and conflating them is the most common way these arguments go wrong.

## Reading the result honestly

The Collatz paper is a proof relative to its declared axioms. A reader who admits
completed infinite carriers can treat the negation of the load-bearing step as a
well-formed object, and for that reader the passage is not established. The paper says
this in its own text. Do not overstate the status of this work to please the author, and
do not manufacture classical objections that the paper has already scoped and answered.
Both failures waste his time; he has said so directly.
