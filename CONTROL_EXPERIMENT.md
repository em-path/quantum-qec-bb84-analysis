# Control Experiment: Quantum Error Correction vs. Classical Redundancy

**Repository:** `em-path/quantum-qec-bb84-analysis`
**Scripts:** `prueba_control.py`, `prueba_control_gemela.py`
**Date:** 2026-11-26
**Subject:** 3-qubit repetition code under a depolarizing channel

---

## Abstract

This report documents a control experiment designed to separate two effects that
are usually bundled together in simulations of quantum error correction (QEC):
(1) the measurement of the error syndrome followed by an active correction, and
(2) the plain redundancy of encoding one logical bit into several physical
qubits followed by a majority vote. The experiment compares both pipelines under
identical noise. For the 3-qubit repetition code, the two pipelines produce
statistically indistinguishable QBER values, and the syndrome-based correction
is never triggered. The result is a formal negative finding: the QBER reduction
observed with this code is a redundancy effect, not evidence of a distinct
quantum correction advantage. A stricter paired (twin) experiment, in which both
scenarios share the same seed, the same noisy state, and the same decoder random
draws, confirms the result: the two scenarios are bit-for-bit identical and the
correction is never triggered.

---

## 1. Motivation and hypothesis

The integrated BB84 + QEC pipeline reports a lower QBER when the repetition code
is used. A natural question is whether that reduction is genuinely produced by
the QEC step (syndrome measurement and correction) or whether it can be
reproduced by redundancy and majority voting alone.

The working hypothesis of the study was that the QEC step is responsible for the
reduction. The control experiment was designed to falsify that hypothesis by
removing only the syndrome/correction step while keeping the encoding, the
channel, and the decoder identical.

---

## 2. Experimental design

Three scenarios were simulated with the same depolarizing channel applied
independently to each physical qubit.

| Scenario | Pipeline | Purpose |
|---|---|---|
| **A — With QEC** | `encode` → `depolarizing_channel_n` → `measure_syndrome` → `correct` → `decode` | Standard QEC pipeline |
| **B — Redundancy only** | `encode` → `depolarizing_channel_n` → `decode` | Removes syndrome measurement and correction; keeps redundancy and majority voting |
| **R — No redundancy** | single qubit → `depolarizing_channel` → `measure_qubit` | Reference baseline without encoding |

The only difference between A and B is the insertion of `measure_syndrome()` and
`correct()`. If QEC contributes to the reduction, A must be significantly better
than B.

### Parameters

| Parameter | Value |
|---|---|
| Code size `n` | 3 physical qubits |
| Noise level `p` | 0.15 per physical qubit |
| Iterations per scenario | 2000 logical bits |
| Channel | Depolarizing, independent per qubit |
| Seeds (A, B, R) | 2026, 2027, 2028 |
| Runtime | Python 3.14, QuTiP 5.x |

For the depolarizing channel used here,
`E(ρ) = (1-p)ρ + (p/3)(XρX + YρY + ZρZ)`, the effective bit-flip probability per
qubit is

\[
q = \frac{2p}{3} = 0.10 .
\]

The factor `2/3` appears because both `X` and `Y` flip the computational-basis
bit, while `Z` does not.

---

## 3. Results

### 3.1 QBER comparison

| Scenario | QBER | Standard error | Errors / iterations |
|---|---:|---:|---:|
| **A) With QEC** (syndrome + correction) | **0.0315** | 0.0039 | 63 / 2000 |
| **B) Redundancy only** (no correction) | **0.0305** | 0.0038 | 61 / 2000 |
| **Difference A − B** | **+0.0010** | 0.0055 | — |
| **R) No redundancy** (`n = 1`) | 0.1055 | 0.0069 | 211 / 2000 |

The difference between A and B is `+0.0010`, with `z = 0.18`. Since
`|z| < 2`, the difference is not statistically significant at the 95 % level.
Section 3.4 repeats the comparison with a strict paired design and confirms the
result.

### 3.2 Mechanism diagnostics (Scenario A)

| Quantity | Count | Fraction |
|---|---:|---:|
| Non-trivial syndromes (error detected) | 0 / 2000 | 0.00 % |
| Effective corrections applied | 0 / 2000 | 0.00 % |

`correct()` did not modify a single state in 2000 iterations.

### 3.3 Comparison with theory

| Quantity | Theoretical value | Observed |
|---|---:|---:|
| QBER without redundancy (`q = 2p/3`) | 0.1000 | 0.1055 |
| QBER with majority of 3 (`3q²(1−q) + q³`) | 0.0280 | 0.0305–0.0315 |

Both observations are consistent with theory within one standard error. The
drop from roughly `0.10` to roughly `0.03` is fully accounted for by the
majority vote over three redundant qubits.

### 3.4 Strict paired (twin) control experiment

The comparison in Section 3.1 used independent seeds for A and B (2026 and 2027).
To rule out the possibility that the similarity of the two QBER values was masked
by different random streams, a stricter paired experiment was run with
`prueba_control_gemela.py`. In this design, both scenarios share, iteration by
iteration:

1. the same logical bit,
2. the same encoded state,
3. the same noisy state `rho_err` (the channel is deterministic), and
4. the same decoder random draws.

Point 4 is enforced by saving the NumPy RNG state before decoding A and restoring
it before decoding B, so both decoders receive identical uniform random numbers.
Any difference between the two scenarios can therefore come only from the state
passed to `decode()`, that is, from the correction itself. The paired analysis
uses the discordant pairs `b` (A correct, B wrong) and `c` (A wrong, B correct),
which is the appropriate test for paired binary outcomes.

Parameters: `n = 3`, `p = 0.15`, `N = 2000`, shared seed `2026`.

| Scenario | QBER | SE | Errors / iterations |
|---|---:|---:|---:|
| **A) With QEC** (syndrome + correction) | **0.0315** | 0.0039 | 63 / 2000 |
| **B) Without QEC** (redundancy only) | **0.0315** | 0.0039 | 63 / 2000 |
| **Difference A − B** | **+0.0000** | 0.0000 | — |

Discordant pairs: `b = 0`, `c = 0`, McNemar-style `z = 0.00`. The decoded bits
of A and B differ in `0 / 2000` iterations: the two scenarios are bit-for-bit
identical.

Per-iteration correction diagnostics:

| Quantity | Count |
|---|---:|
| Non-trivial syndromes (error detected) | 0 / 2000 |
| Corrections that changed the state | 0 / 2000 |
| **Correction triggered** (both conditions) | **0 / 2000** |
| Syndrome non-trivial but state unchanged | 0 / 2000 |
| State changed without a non-trivial syndrome | 0 / 2000 |

The exact equality is the expected outcome when the correction is a no-op: both
scenarios receive the same state and the same random draws, so their decoded bits
coincide by construction. The paired experiment confirms that the similarity in
Section 3.1 is not a statistical artifact and that the syndrome-based correction
is never executed. As explained in Section 5, this is a deterministic
consequence of the expectation-value syndrome, not an effect of the seed. The
physical conclusion of Section 4 therefore holds: for this code, single-error
syndrome correction and majority voting are operationally equivalent.

---

## 4. Physical conclusion

> **"For the 3-qubit repetition code, measuring the syndrome and majority voting
> are mathematically equivalent. The control experiment shows that the reduction
> in QBER comes from the structured redundancy of the code, not from a magical
> correction effect. A true QEC advantage would require a code that corrects both
> X and Z errors (e.g., Steane's code)."**

The equivalence can be seen directly. In the Z basis, a single bit-flip is
corrected by the syndrome in exactly the same way that a majority vote corrects
it: the flipped qubit is outvoted by the other two. If two or three qubits flip,
both procedures fail. Consequently, for this code and this noise model,

\[
\mathrm{QBER}_{A} = \mathrm{QBER}_{B}
= 3q^{2}(1-q) + q^{3}.
\]

The experiment therefore does **not** support the claim that the reduction is
produced by a distinct quantum correction mechanism. It supports the weaker and
more precise statement that the reduction is produced by the **structured
redundancy** of the repetition code together with a majority decision rule.

---

## 5. Note on the implementation of `medir_sindrome()`

The function `medir_sindrome()` (Spanish tree) / `measure_syndrome()` (English
package) does not perform a projective single-shot measurement. It computes the
expectation value of each stabilizer generator,

\[
\langle g_i \rangle = \mathrm{Tr}(\rho\, Z_i Z_{i+1}),
\]

and assigns syndrome bit `0` when the expectation is positive and `1` when it is
negative. This is a **mean-value proxy**, not a collapse to a definite syndrome
outcome.

For the state produced by independent depolarizing noise, the qubits remain in a
product state and

\[
\langle Z_i Z_{i+1} \rangle
= \langle Z_i \rangle \langle Z_{i+1} \rangle
= (1-2q)^2 = 0.64 > 0
\]

at `p = 0.15`. The proxy therefore returns the trivial syndrome `(0, 0)` in every
iteration, which is why `correct()` never acts. The same behaviour holds for any
`p < 0.75` (equivalently `q < 0.5`); it is not a statistical fluctuation and it
does not depend on the random seed.

This implementation detail explains the `0 / 2000` correction count and should
be acknowledged as a limitation of the current simulator. However, it does not
invalidate the physical conclusion. Even with a genuine projective syndrome
measurement, the decoded-bit statistics of the 3-qubit repetition code would be
the same, because correcting a single bit-flip is operationally identical to
majority voting. The proxy affects the **attribution of the mechanism inside the
code**; it does not affect the **equivalence** between syndrome correction and
majority voting for this code.

A genuine QEC advantage would require both:

1. a code that protects against both bit-flip (`X`) and phase (`Z`) errors —
   for example, the Steane code, the Shor code, or a surface code; and
2. a projective (single-shot) syndrome measurement, so that the correction acts
   on definite error events rather than on mean values.

---

## 6. Reproducibility

Run from the repository root:

```bash
python prueba_control.py 2000 0.15 3 2026
python prueba_control_gemela.py 2000 0.15 3 2026
```

The arguments are, in order: iterations, noise level `p`, code size `n`, and
seed. The first script prints the independent-seed comparison; the second prints
the strict paired (twin) comparison. Neither writes or modifies any file.

Both scripts include a compatibility import shim so that the same files run
against both module naming conventions:

- Spanish working tree: `src/qec.py` (`codificar`, `medir_sindrome`, `corregir`,
  `decodificar`), `src/simulacion.py`, `src/canal.py`.
- English reproducible package: `src/qec.py` (`encode`, `measure_syndrome`,
  `correct`, `decode`), `src/simulation.py`, `src/channel.py`.

The underlying physics is identical in both trees; only the identifiers differ.

---

## 7. Implications and limitations

- **Reframe the claim.** The repetition code reduces the QBER through redundancy
  and majority voting. This is a real and useful protection against bit-flip
  noise, but it is not evidence of a distinct quantum correction advantage.
- **Do not attribute the reduction to the syndrome step.** In the current
  simulator the syndrome step is inert for this noise model, and even a correct
  projective implementation would be equivalent to majority voting for this
  code.
- **Use the result as a control, not as a failure.** The negative result
  strengthens the rigor of the study: it identifies precisely which part of the
  pipeline produces the improvement and prevents an overstatement in the thesis.
- **The paired design rules out a seed artifact.** With a shared seed, shared
  noisy states, and shared decoder random draws, A and B are bit-for-bit
  identical. The absence of a correction effect is therefore a property of the
  code and of the simulator, not of the random sampling.
- **Limitations.** The experiment uses a single code size (`n = 3`), a single
  noise level (`p = 0.15`), and a bit-flip-only repetition code. The conclusion
  is specific to this code and channel. It does not rule out a genuine QEC
  advantage for codes that correct both `X` and `Z` errors.

---

## 8. Summary table

| Question | Answer |
|---|---|
| Does QEC reduce the QBER more than redundancy alone? | No. A and B are statistically identical (Section 3.1) and bit-for-bit identical in the paired experiment (Section 3.4). |
| Did the syndrome/correction step act at all? | No. 0 of 2000 corrections, including 0 triggered corrections in the paired experiment. |
| Where does the reduction come from? | Structured redundancy (`n = 3`) plus majority voting. |
| Is the current syndrome measurement projective? | No. It is an expectation-value proxy. |
| Does that invalidate the equivalence conclusion? | No. Syndrome correction and majority voting are equivalent for this code. |
| What would demonstrate a genuine QEC advantage? | A code correcting both `X` and `Z` (e.g., Steane) with projective syndrome measurement. |
