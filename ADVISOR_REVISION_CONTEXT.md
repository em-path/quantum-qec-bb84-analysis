# Advisor Revision — Context and Findings

**Date:** 2026-11-27
**Repository:** <https://github.com/em-path/quantum-qec-bb84-analysis>
**Baseline:** remote `main` at `0cecfa8`; report 52 pages; IEEE article 5 pages.
**Scope:** `documento-final/reporte-final.tex` and
`documento-final/articulo_ieee.tex` (local); repository copies under `report/`.

This note tracks the context, the empirical findings, and the edits applied after
the advisor's review. It is written in English because it is repository
management material; the thesis document itself remains in Spanish.

---

## 1. Advisor feedback

1. Move the control experiment out of the limitations and into the Results
   section as a new subsection 3.3.4.
2. Explain its significance in the Discussion (3.4).
3. Correct the Conclusions (3.5) so they do not overstate the role of QEC.
4. Keep Master's-level rigor while remaining accessible to a general audience,
   reusing the established analogies (e.g., the security guards).
5. Apply the same adjustments to the IEEE article.
6. Compile without LaTeX errors and publish to GitHub.

---

## 2. Context reviewed

- **Thesis objective:** quantify the trade-off between quantum error correction
  (QEC) and the effective secure-key rate of BB84 under a depolarizing channel,
  and identify the optimal repetition-code size `n = 3, 5, 7` as a function of
  the noise level `p`.
- **Control experiment design:** scenario A runs the full pipeline
  (`encode → channel → syndrome → correct → decode`); scenario B keeps
  `encode → channel → decode` and removes only the syndrome and correction.
  A third reference (`n = 1`) measures the channel without redundancy.
- **Strict paired protocol:** shared seed `2026`, identical logical bits,
  identical noisy states, and identical decoder random draws (the NumPy RNG
  state is saved and restored). Any difference can only come from correction.
- **Sources:** `CONTROL_EXPERIMENT.md`, `SESSION_CONTEXT.md`,
  `control_experiment/control_experiment.py`,
  `control_experiment/twin_control_experiment.py`, and
  `data/resultados_finales.csv`.

**Observation:** the current report's "Limitaciones y recomendaciones" section
did not actually describe the control experiment; it only listed the bit-flip
scope of the code. The full experiment is therefore added to Results, and the
limitations keep only scoped caveats derived from it.

---

## 3. Findings

Parameters: `n = 3`, `p = 0.15`, `N = 2000` logical bits, depolarizing channel
independent per qubit. The effective bit-flip probability is
`q = 2p/3 = 0.10`.

| Scenario | QBER | Standard error | Errors / N |
|---|---:|---:|---:|
| A) With QEC (syndrome + correction) | 0.0315 | 0.0039 | 63 / 2000 |
| B) Without QEC (redundancy only) | 0.0315 | 0.0039 | 63 / 2000 |
| Difference A − B | 0.0000 | 0.0000 | 0 |
| Reference without redundancy (`n = 1`) | 0.1055 | 0.0069 | 211 / 2000 |

- Discordant pairs: `b = 0`, `c = 0`; the decoded bits differ in `0 / 2000`
  iterations.
- Non-trivial syndromes: `0 / 2000`; effective corrections: `0 / 2000`.
- Theoretical majority-vote QBER: `3q²(1−q) + q³ = 0.028`, compatible with the
  observed `0.0315` within sampling error.
- **Physical conclusion:** for the 3-qubit repetition code, syndrome correction
  and majority voting are operationally equivalent. The QBER reduction comes
  from structured redundancy, not from a distinct correction mechanism.
- **Implementation caveat:** the current syndrome routine thresholds expectation
  values, so it is trivially zero for the depolarized product state at
  `p < 0.75`. This affects the mechanism attribution inside the simulator but
  not the equivalence, which also holds for a projective syndrome measurement.

---

## 4. Edits applied

### `documento-final/reporte-final.tex`

- New subsection **3.3.4** "Experimento de control: redundancia clásica vs.
  corrección cuántica", with the comparative table (`tab:control`) and the
  theoretical equivalence equation (`eq:control`).
- New Discussion (3.4) paragraph on the equivalence and the real scope of the
  contribution.
- Rewritten Conclusions (3.5) to distinguish structural redundancy from syndrome
  correction.
- Limitations (3.6) reduced to scoped caveats plus future work (Steane-style
  codes and projective syndrome measurement).

### `documento-final/articulo_ieee.tex`

- New Results subsection "Experimento de control: redundancia vs. corrección",
  with a compact table and equation.
- New "Implicaciones" paragraph on the equivalence and future work.
- Adjusted Conclusion to attribute the reduction to redundancy.
- Added the Steane (1996) reference used by the new paragraph.

### Repository

- `CHANGELOG.md` updated with version 1.1.0.
- `report/` regenerated (report TeX/PDF, and IEEE article source/PDF).
- Control scripts moved to `control_experiment/` and renamed in English; the
  Markdown context is mirrored in `agent-context/` (see
  `agent-context/LAST_RESULTS.md`).

---

## 5. Verification

- [x] Report compiles with `latexmk` and no LaTeX errors: **56 pages**, exit 0.
- [x] IEEE article compiles with `latexmk` and no LaTeX errors: **6 pages**,
      exit 0.
- [x] New table and text fit within the margins (visually checked in the
      rendered PDFs); the table was allowed to float to avoid a large gap.
- [x] Commit and push to `origin/main` succeeded.

**Publication:** release commit `656e57f`, tag `v1.1.0`, pushed to
`origin/main` on 2026-11-27.

Compilation commands (from the respective directories):

```text
latexmk -pdf -interaction=nonstopmode -halt-on-error reporte-final.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error articulo_ieee.tex
```

The repository copy of the report was also recompiled from `report/` after
reapplying the two `../src/` listing paths; it produced 56 pages with no errors.
