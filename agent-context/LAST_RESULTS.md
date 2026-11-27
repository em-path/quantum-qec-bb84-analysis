# Latest Results and Context

**Date:** 2026-11-27
**Repository:** <https://github.com/em-path/quantum-qec-bb84-analysis>
**Release:** `v1.2.0` (publication recorded below after the push)
**Previous release:** `v1.1.0` (`656e57f`)

This note is the current handoff context. It complements `SESSION_CONTEXT.md`
and `ADVISOR_REVISION_CONTEXT.md`.

---

## 1. Control-experiment finding

Parameters: `n = 3`, `p = 0.15`, `N = 2000` logical bits, seed `2026`,
depolarizing channel independent per physical qubit. The effective bit-flip
probability is `q = 2p/3 = 0.10`.

| Scenario | QBER | Standard error | Errors / N |
|---|---:|---:|---:|
| A) With QEC (syndrome + correction) | 0.0315 | 0.0039 | 63 / 2000 |
| B) Without QEC (redundancy only) | 0.0315 | 0.0039 | 63 / 2000 |
| Difference A − B | 0.0000 | 0.0000 | 0 |
| Reference without redundancy (`n = 1`) | 0.1055 | 0.0069 | 211 / 2000 |

Key findings:

- The two scenarios are bit-for-bit identical: `0 / 2000` discordant pairs.
- The syndrome was trivial in `2000 / 2000` iterations; the correction changed
  no state.
- The theoretical majority-vote QBER is `3q²(1−q) + q³ = 0.028`, compatible
  with the observed `0.0315` within sampling error.
- For the 3-qubit repetition code, syndrome correction and majority voting are
  operationally equivalent. The QBER reduction comes from structural redundancy,
  not from a distinct correction mechanism.
- Implementation caveat: the simulator thresholds stabilizer expectation values,
  so the syndrome is trivially zero for the depolarized product state at
  `p < 0.75`. The equivalence also holds for a projective syndrome measurement.

---

## 2. Advisor revision integrated (`v1.1.0`)

Report (`documento-final/reporte-final.tex`):

- New **3.3.4** “Experimento de control: redundancia clásica vs. corrección
  cuántica”, with the comparative table and the equivalence equation.
- Discussion (3.4) explains the equivalence and the real scope of the
  contribution: the value is the overhead/key-rate trade-off, not a “magical”
  QEC superiority.
- Conclusions (3.5) rewritten to attribute the reduction to structural
  redundancy.
- Limitations (3.6) reduced to scoped caveats plus future work (Steane-style
  codes and projective syndrome measurement).

IEEE article (`documento-final/articulo_ieee.tex`):

- New Results subsection **IV-E** with Table III and equation (7).
- New “Implicaciones” paragraph on the equivalence and future work.
- Conclusion adjusted with the same nuance; Steane (1996) reference added.
- The article is now **6 pages** (was 5); the report appendix description was
  updated to “seis páginas” and “tres tablas”.

The old limitations section did **not** actually describe the control
experiment; the full treatment was added to Results, and the limitations kept
only scoped caveats.

---

## 3. Folder restructure (`v1.2.0`)

- `control_experiment/` now contains:
  - `control_experiment.py` (independent-seed comparison),
  - `twin_control_experiment.py` (strict paired comparison),
  - `README.md`.
- The former Spanish-named scripts were removed from the repository root:
  - `prueba_control.py` → `control_experiment/control_experiment.py`
  - `prueba_control_gemela.py` →
    `control_experiment/twin_control_experiment.py`
- Both scripts now add the repository root to `sys.path`, so they can be run
  from any working directory.
- `agent-context/` mirrors the project's Markdown context; this file records the
  latest results.
- Links were updated in `CONTROL_EXPERIMENT.md`, `SESSION_CONTEXT.md`,
  `ADVISOR_REVISION_CONTEXT.md`, `README.md`, the report (Table 3.2 and
  Appendix A.2), and the IEEE article (Section IV-E).

---

## 4. Compilation and verification

| Item | Result |
|---|---|
| `reporte-final.tex` | **56 pages**, exit 0, no LaTeX errors |
| `articulo_ieee.tex` | **6 pages**, exit 0, no LaTeX errors |
| `control_experiment.py` | Tested with `N = 100`, exit 0 |
| `twin_control_experiment.py` | Tested with `N = 100`, exit 0 |
| Repository report copy | Recompiled from `report/`, 56 pages |

The only remaining overfull-box warning is a pre-existing 12.3 pt warning
unrelated to the new content. The control table fits within the margins, and its
caption includes the data source.

---

## 5. Git state

- Release commit and tag: recorded after the publication push.
- Repository files: `report/reporte-final.tex` and `.pdf`,
  `report/articulo_ieee.tex` and `.pdf`, `control_experiment/`, `agent-context/`,
  `CHANGELOG.md`.

---

## 6. Recommended next steps

1. Implement a genuinely projective syndrome measurement and rerun the
   experiment.
2. Evaluate codes that correct both `X` and `Z` errors (Steane, Shor, or surface
   codes) with the same paired methodology.
3. Recompute `R_efectiva` for `n = 3, 5, 7` under the projective model and
   compare with `data/resultados_finales.csv`.
4. Update the README and this context note whenever a new experiment is added.

---

## 7. Canonical documents

- Report: `../documento-final/reporte-final.tex`
- IEEE article: `../documento-final/articulo_ieee.tex`
- Control experiment: `../CONTROL_EXPERIMENT.md`
- Scripts: `../control_experiment/`
- Changelog: `../CHANGELOG.md`
