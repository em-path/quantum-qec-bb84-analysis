# Quantum QEC BB84 Analysis

A reproducible simulation package for studying **quantum error correction (QEC)** and the **secret-key rate of the BB84 protocol** under depolarizing noise.

The project compares repetition codes of different sizes (`n = 1, 3, 5, 7`, where `n = 1` means no QEC) and quantifies the trade-off between error suppression and the physical-qubit overhead. For every channel error probability `p`, it computes:

- the **Quantum Bit Error Rate (QBER)** after sifting,
- the **gross secret-key rate** `R = 1 - 2 H2(QBER)`, based on the Shor-Preskill bound,
- the **effective secret-key rate** `R_eff = R / n`, which accounts for the cost of the repetition code,
- the **optimal code size** for each noise level.

## Repository layout

| Path | Contents |
|---|---|
| `reproduction_package/` | Self-contained simulation package (English). |
| `control_experiment/` | Control-experiment scripts and README. |
| `report/` | LaTeX sources and PDFs of the final report and IEEE article. |
| `agent-context/` | Markdown context snapshots and the latest findings. |
| `CONTROL_EXPERIMENT.md` | Full control-experiment report. |
| `CHANGELOG.md` | Release history (English). |

## Project structure

```
reproduction_package/
├── src/
│   ├── channel.py       # Depolarizing channel model
│   ├── bb84.py          # BB84 without QEC
│   ├── qec.py           # Repetition code: encoding, syndromes, correction
│   └── simulation.py    # Integrated BB84 + QEC pipeline and parameter sweep
├── scripts/
│   ├── run_simulation.py    # Runs the final sweep (N = 10000)
│   └── generate_figures.py  # Regenerates all figures and the optimal-n table
├── data/
│   ├── final_results.csv    # Sweep results for (p, n)
│   └── optimal_n.csv        # Optimal code size per noise level
├── figs/                    # Generated figures (PNG, 300 DPI)
├── requirements.txt
├── .gitignore
└── README.md
```

## Control experiment

The `control_experiment/` folder contains two standalone scripts:

- `control_experiment.py` — independent-seed comparison of QEC vs. redundancy.
- `twin_control_experiment.py` — strict paired comparison with shared seed,
  state, and decoder draws.

Run them from the repository root:

```bash
python control_experiment/control_experiment.py 2000 0.15 3 2026
python control_experiment/twin_control_experiment.py 2000 0.15 3 2026
```

For `n = 3`, `p = 0.15`, and `N = 2000`, both scenarios give QBER `0.0315` with
zero syndrome-triggered corrections. See
[`CONTROL_EXPERIMENT.md`](CONTROL_EXPERIMENT.md) for the full analysis.

## Requirements

- Python 3.10 or newer (tested with Python 3.14)
- QuTiP 5.x, NumPy, SciPy, Matplotlib, pandas, and seaborn

## Installation

From the root of `reproduction_package/`, create a virtual environment (recommended) and install the dependencies:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

## Running the simulation

Run all commands from the root of `reproduction_package/` so that the relative data paths resolve correctly.

The full sweep uses `N = 10000` logical bits per `(p, n)` combination and can take **20 to 40 minutes**:

```bash
python scripts/run_simulation.py
```

This writes `data/final_results.csv` with one row per `(p, n)` pair and the following columns:

| Column | Description |
| --- | --- |
| `p` | Error probability per physical qubit |
| `n` | Repetition-code size (`1`, `3`, `5`, `7`) |
| `qber` | Quantum Bit Error Rate after sifting |
| `n_sifted` | Number of bits kept after basis sifting |
| `gross_rate` | `1 - 2 H2(QBER)` |
| `effective_rate` | `gross_rate / n` |

For a quick check with a smaller sample, call the sweep directly:

```python
from src.simulation import parameter_sweep

parameter_sweep(N=1000, csv_path="data/final_results.csv")
```

## Regenerating the figures

After `data/final_results.csv` exists, regenerate all figures and the optimal-code table:

```bash
python scripts/generate_figures.py
```

This produces:

- `figs/qber_vs_p.png` — QBER versus `p` for each code size, with the BB84 security threshold (`QBER = 0.11`).
- `figs/tasa_efectiva_vs_p.png` — effective secret-key rate versus `p`.
- `figs/mapa_calor.png` — heatmap of `R_eff` over `p × n`.
- `data/optimal_n.csv` — optimal `n` and its effective rate for every noise level.

The plotting script accepts both the current English column names and the legacy Spanish names, so older result files remain compatible.

## Validating the modules

Each core module includes a self-contained validation block:

```bash
python -m src.channel
python -m src.bb84
python -m src.qec
```

`src/qec.py` also runs unit tests for encoding, syndrome detection, correction, and behavior at extreme noise.

## Reproducibility notes

- The simulation uses NumPy's global random number generator. Set `np.random.seed(<value>)` before a run to make results reproducible.
- Figures are saved at 300 DPI in an academic style suitable for publication.
- All paths are relative to the package root; run scripts from `reproduction_package/`.

## References

- Bennett, C. H., & Brassard, G. (1984). Quantum cryptography: Public key distribution and coin tossing.
- Nielsen, M. A., & Chuang, I. L. (2010). *Quantum Computation and Quantum Information*.
- Shor, P. W., & Preskill, J. (2000). Simple proof of security of the BB84 quantum key distribution protocol.
- Gottesman, D. (1997). *Stabilizer codes and quantum error correction*.
