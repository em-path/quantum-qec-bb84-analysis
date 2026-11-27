# Session Context — QEC / BB84 PIA

**Last updated:** 2026-11-27
**Repository:** <https://github.com/em-path/quantum-qec-bb84-analysis>
**Remote `main`:** `5714aea` (verified 2026-11-27)
**Local project root:** `C:\Users\neosa\Documents\Maestria_Ciberseguridad_UTM\proyecto-ciber-2026\PIA_QEC_BB84`

**Structure update (2026-11-27):** the control scripts were moved to
`control_experiment/` and renamed in English; the former Spanish filenames are
retired. All Markdown context is mirrored in `agent-context/`, and the latest
results are recorded in `agent-context/LAST_RESULTS.md`.

This file is a handoff note for a new session. It summarizes what was done, what
was found, where the artifacts are, and what remains open. It complements
`AGENTS.md`, which describes the thesis rules and repository conventions.

---

## 1. Executive summary

- The investigation is the PIA UTM project on **quantum error correction (QEC)
  and the secure-key rate of BB84 under noisy channels**.
- This session designed and ran a **control experiment** to determine whether the
  QBER reduction observed with the repetition code comes from the **syndrome
  measurement + correction** or only from **redundancy + majority voting**.
- **Main finding:** for the 3-qubit bit-flip repetition code, syndrome correction
  and majority voting are mathematically equivalent. The QBER reduction is a
  **structured-redundancy effect**, not evidence of a distinct quantum correction
  advantage.
- The current simulator's `measure_syndrome()` uses expectation values instead of
  a projective measurement. For the depolarized product state at `p = 0.15`, the
  syndrome is always `(0,0)`, so `correct()` never fires. This is deterministic,
  not a seed artifact.
- A **strict paired (twin) experiment** with the same seed, same bits, same noisy
  state, and same decoder random draws produced **bit-for-bit identical** results
  for QEC enabled vs disabled, with **0/2000** corrections triggered.

---

## 2. Project objective (from `AGENTS.md`)

Thesis topic: *"Corrección de errores cuánticos y tasa de clave segura en el
protocolo BB84 bajo canales ruidosos."* The broader goal is to identify the
optimal QEC code size (`n = 3, 5, 7`) that maximizes the effective key rate
`R_efectiva` under different noise levels `p`.

This session did **not** modify the physics logic of `src/canal.py`,
`src/bb84.py`, or `src/qec.py`. All new work is additive.

---

## 3. What was done in this session

1. Inspected the original modules:
   - `src/qec.py`: `codificar`, `medir_sindrome`, `corregir`, `decodificar`.
   - `src/canal.py`: `canal_depolarizante`, `canal_depolarizante_n`.
   - `src/simulacion.py`: integrated BB84 + QEC pipeline.
   - `src/bb84.py`: `preparar_qubit`, `medir_qubit`.
2. Detected that `medir_sindrome()` computes stabilizer expectation values
   `Tr(ρ Z_i Z_{i+1})` and thresholds their sign. On the mixed state produced by
   the depolarizing channel, this returns the trivial syndrome for `p < 0.75`.
3. Created `control_experiment/control_experiment.py`: independent-seed comparison of
   - **A** = full QEC pipeline,
   - **B** = redundancy only (no syndrome, no correction),
   - **R** = no redundancy (`n = 1`).
4. Created `CONTROL_EXPERIMENT.md`: formal report of the control experiment,
   including the physical conclusion and the implementation caveat.
5. Translated `control_experiment/control_experiment.py` fully to English and added a compatibility
   import shim for the Spanish and English module names.
6. Created `control_experiment/twin_control_experiment.py`: strict paired ("twin") experiment with a
   single shared seed, identical bits, identical noisy states, and identical
   decoder random draws (NumPy RNG state saved/restored around the two decodes).
7. Added **Section 3.4** to `CONTROL_EXPERIMENT.md` documenting the paired
   experiment.
8. Pushed the new scripts and report updates to GitHub (see Section 8).

---

## 4. Key results

Parameters common to all runs: `n = 3`, `p = 0.15`, `N = 2000` logical bits,
depolarizing channel independent per physical qubit. The effective per-qubit
bit-flip probability is

```text
q = 2p/3 = 0.10
```

because both `X` and `Y` flip the computational-basis bit, while `Z` does not.

### 4.1 Independent-seed control (`control_experiment/control_experiment.py`)

Seeds: A = 2026, B = 2027, R = 2028.

| Scenario | QBER | SE | Errors / N |
|---|---:|---:|---:|
| A) With QEC (syndrome + correction) | 0.0315 | 0.0039 | 63 / 2000 |
| B) Redundancy only (no correction) | 0.0305 | 0.0038 | 61 / 2000 |
| Difference A − B | +0.0010 | 0.0055 | — |
| R) No redundancy (`n = 1`) | 0.1055 | 0.0069 | 211 / 2000 |

- `z = 0.18`, so the A/B difference is **not significant** (`|z| < 2`).
- Non-trivial syndromes: **0/2000**. Effective corrections: **0/2000**.
- Theory: no redundancy `q = 0.1000`; majority of 3
  `3q²(1−q) + q³ = 0.0280`. Both observations are within one standard error.

### 4.2 Strict paired / twin control (`control_experiment/twin_control_experiment.py`)

Shared seed: 2026 for A and B; reference seed 2028 for R.

| Scenario | QBER | SE | Errors / N |
|---|---:|---:|---:|
| A) With QEC | 0.0315 | 0.0039 | 63 / 2000 |
| B) Without QEC | 0.0315 | 0.0039 | 63 / 2000 |
| Difference A − B | +0.0000 | 0.0000 | — |

- Discordant pairs: `b = 0` (A correct, B wrong), `c = 0` (A wrong, B correct);
  McNemar-style `z = 0.00`.
- Decoded bits differing between A and B: **0/2000**.
- Non-trivial syndromes: **0/2000**.
- Corrections that changed the state: **0/2000**.
- **Correction triggered (both conditions): 0/2000.**
- Reference: `n = 1` gives QBER = 0.1055.

---

## 5. Physical conclusion

The exact conclusion recorded in `CONTROL_EXPERIMENT.md` is:

> **"For the 3-qubit repetition code, measuring the syndrome and majority voting
> are mathematically equivalent. The control experiment shows that the reduction
> in QBER comes from the structured redundancy of the code, not from a magical
> correction effect. A true QEC advantage would require a code that corrects both
> X and Z errors (e.g., Steane's code)."**

Why this holds:

- In the Z basis, a single bit-flip is corrected by the syndrome in exactly the
  same way as by a majority vote: the flipped qubit is outvoted.
- Two or three flips defeat both procedures.
- Therefore, for this code and channel,
  `QBER_A = QBER_B = 3q²(1−q) + q³`.

### 5.1 Implementation caveat

`measure_syndrome()` (English) / `medir_sindrome()` (Spanish) is a **mean-value
proxy**, not a projective single-shot measurement. It computes
`⟨g_i⟩ = Tr(ρ Z_i Z_{i+1})` and assigns syndrome bit `0` if the expectation is
positive and `1` if negative.

For the depolarized product state,

```text
⟨Z_i Z_{i+1}⟩ = (1 − 2q)² = 0.64 > 0   at p = 0.15
```

so the syndrome is `(0,0)` for every `p < 0.75` (equivalently `q < 0.5`). This is
deterministic and seed-independent. It explains the `0/2000` correction count.

This caveat affects the **mechanism attribution inside the simulator**, but not
the **equivalence conclusion**: even a genuine projective syndrome measurement
would give the same decoded-bit statistics for the 3-qubit repetition code.

---

## 6. File map and roles

### New files created this session

| File | Role |
|---|---|
| `control_experiment/control_experiment.py` | Independent-seed control experiment (A vs B vs R). English. CLI. |
| `control_experiment/twin_control_experiment.py` | Strict paired/twin experiment (same seed and same decoder draws). English. CLI. |
| `CONTROL_EXPERIMENT.md` | Formal report: motivation, design, results, physical conclusion, caveat, reproducibility, Section 3.4 paired experiment. |

Both scripts:

- import English names first (`encode`, `measure_syndrome`, `correct`, `decode`,
  `src.simulation`, `src.channel`) and fall back to Spanish names
  (`codificar`, `medir_sindrome`, `corregir`, `decodificar`, `src.simulacion`,
  `src.canal`);
- print only; they do not write or modify files;
- accept CLI arguments: `iterations`, `p`, `n`, `seed`.

### Original project files (not modified)

- `src/qec.py`, `src/canal.py`, `src/simulacion.py`, `src/bb84.py`
- `data/`, `figs/`, `scripts/`, `documento-final/`, `protocolo/`, `contexto/`

### Remote English package

The GitHub repository is an English reproducible package with different
filenames:

| Local Spanish tree | Remote English package |
|---|---|
| `src/qec.py` (`codificar`, `medir_sindrome`, `corregir`, `decodificar`) | `src/qec.py` (`encode`, `measure_syndrome`, `correct`, `decode`) |
| `src/simulacion.py` | `src/simulation.py` |
| `src/canal.py` | `src/channel.py` |
| `src/bb84.py` (`preparar_qubit`, `medir_qubit`) | `src/bb84.py` (`prepare_qubit`, `measure_qubit`) |

The compatibility shim in both scripts makes the same file run in both trees.

---

## 7. How to reproduce

### Python environment

The default `python` on this machine is **3.15 and does not have QuTiP**. Use the
Python 3.14 interpreter that does:

```text
C:\Users\neosa\AppData\Local\Python\pythoncore-3.14-64\python.exe
```

Verified versions: QuTiP 5.3.1, NumPy 2.5.3, pandas 3.0.6.

### Commands (from the project root)

```powershell
& "C:\Users\neosa\AppData\Local\Python\pythoncore-3.14-64\python.exe" control_experiment/control_experiment.py 2000 0.15 3 2026
& "C:\Users\neosa\AppData\Local\Python\pythoncore-3.14-64\python.exe" control_experiment/twin_control_experiment.py 2000 0.15 3 2026
```

Arguments: iterations, `p`, `n`, seed. The second command prints the paired
comparison and the per-iteration correction diagnostics.

---

## 8. Git state and workflow

- The local project root **is not a Git repository**.
- The remote `main` is at **`5714aea`**.
- Commits pushed in this session:

| Commit | Message |
|---|---|
| `8cacf0a` | Feat: Added control experiment and analysis on the equivalence of repetition codes and majority voting |
| `d3474f8` | Refactor: Translate control experiment script to English |
| `e38a648` | Feat: Add strict paired control experiment for QEC vs majority voting |
| `5714aea` | Docs: Add strict paired experiment section to control report |

- The commits were made from a temporary clone at
  `C:\Users\neosa\AppData\Local\Temp\opencode\qqec-remote-inspect`. This path is
  temporary and may disappear; the remote repository is the source of truth.
- To push future changes without touching the local Spanish tree, copy the
  changed files into a fresh clone of the remote, then `git add`, `git commit`,
  and `git push origin main`.
- If the project root should become a permanent repo tracking `origin/main`,
  that setup was **not** done and remains an open decision.

---

## 9. Open questions and recommended next steps

1. **Integrate the negative result into the thesis.** Decide whether it belongs in
   Chapter III (Results and discussion) as a control/limitation, and adjust any
   claim that attributes the QBER reduction to the syndrome correction.
2. **Implement a true projective syndrome measurement.** Sample the syndrome
   according to the state (or simulate the error pattern) instead of thresholding
   an expectation value. Keep it in a new file; do not modify the original
   `qec.py` without consultation.
3. **Test a code that corrects both `X` and `Z`.** The Steane code, the Shor
   code, or a surface code would allow a genuine QEC-advantage comparison. This
   is the natural next experiment for the thesis.
4. **Re-evaluate `R_efectiva` for `n = 3, 5, 7`** under the corrected
   (projective) model and compare with the current `data/resultados_finales.csv`.
5. **Update the README / reproduction package** to include the control
   experiments and the paired result.
6. **Decide on repository structure.** The local Spanish tree and the remote
   English package use different filenames. The scripts handle both, but the
   duplication should eventually be resolved.
7. **Optionally update `CONTROL_EXPERIMENT.md`** if new experiments (projective
   syndrome, Steane code) are added.

---

## 10. Reminders and constraints

- Follow `AGENTS.md`: do not modify the physics logic of `src/canal.py`,
  `src/bb84.py`, or `src/qec.py` without consulting.
- The thesis is in Spanish, APA 7, UTM format; equations and figures must be
  numbered and referenced.
- Do not make unsupported claims: numerical results must be backed by `data/` or
  by reproducible scripts.
- The current control experiment is a **negative result** and should be reported
  honestly, not hidden or reframed as a success.
- The user alternates between Spanish and English; the code and the two control
  reports are currently in English.

---

## 11. Quick orientation for a new session

If you only read one thing, read this:

- The repetition code's QBER reduction is **redundancy + majority voting**, not a
  syndrome-correction advantage.
- The paired experiment shows **A = B = 0.0315** with **0/2000** corrections.
- The syndrome is always `(0,0)` because `measure_syndrome()` uses expectation
  values; this is an implementation limitation.
- Next meaningful step: a **projective syndrome measurement** and a code that
  corrects both `X` and `Z` (e.g., **Steane**), then compare `R_efectiva`.
