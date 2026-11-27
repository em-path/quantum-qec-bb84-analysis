# Control Experiment: QEC vs. Classical Redundancy

This folder contains the two standalone scripts that support the control
experiment described in [`../CONTROL_EXPERIMENT.md`](../CONTROL_EXPERIMENT.md)
and in Section 3.3.4 of the final report.

| Script | Purpose |
|---|---|
| `control_experiment.py` | Independent-seed comparison of A (QEC), B (redundancy only), and R (no redundancy). |
| `twin_control_experiment.py` | Strict paired comparison: same seed, same logical bit, same noisy state, and same decoder random draws. |

## Key result

Parameters: `n = 3`, `p = 0.15`, `N = 2000`, seed `2026`.

| Scenario | QBER | Standard error | Errors / N |
|---|---:|---:|---:|
| A) With QEC (syndrome + correction) | 0.0315 | 0.0039 | 63 / 2000 |
| B) Without QEC (redundancy only) | 0.0315 | 0.0039 | 63 / 2000 |
| Reference without redundancy (`n = 1`) | 0.1055 | 0.0069 | 211 / 2000 |

The two scenarios are bit-for-bit identical, and the syndrome was trivial in
`2000 / 2000` iterations. For the 3-qubit repetition code, syndrome correction
and majority voting are operationally equivalent: the QBER reduction comes from
structural redundancy, not from a distinct correction mechanism.

## Running the scripts

From the repository root:

```bash
python control_experiment/control_experiment.py 2000 0.15 3 2026
python control_experiment/twin_control_experiment.py 2000 0.15 3 2026
```

Arguments, in order: iterations, `p`, `n`, and seed. The scripts only print to
the screen; they do not write or modify files. Each script adds the repository
root to `sys.path`, so it can be launched from any working directory.

## Requirements

- Python 3.14 or newer
- NumPy
- QuTiP 5.x (used by `src/`)

The scripts import the English package (`encode`, `measure_syndrome`, `correct`,
`decode`) first and fall back to the Spanish working-tree names when needed.

## Related documents

- Full experiment report: [`../CONTROL_EXPERIMENT.md`](../CONTROL_EXPERIMENT.md)
- Thesis section: `../documento-final/reporte-final.tex` (local) or
  `../report/reporte-final.tex` (repository), Section 3.3.4
- Latest context snapshot: [`../agent-context/LAST_RESULTS.md`](../agent-context/LAST_RESULTS.md)
