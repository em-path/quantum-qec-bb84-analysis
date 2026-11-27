"""
control_experiment.py - Control experiment: QEC vs. classical redundancy
=====================================================================

Experimental question
---------------------
The QBER reduction observed in the QEC pipeline: is it caused by the
SYNDROME MEASUREMENT + quantum CORRECTION, or is plain REDUNDANCY
(repeating the qubit n times) plus MAJORITY VOTING in the decoder enough?

Design
------
The same N logical bits are transmitted through the same depolarizing
channel (probability p per physical qubit) in two scenarios that differ
in a single step:

    A) With QEC ....... encode -> noise -> measure_syndrome ->
                        correct -> decode (majority)
    B) Redundancy only  encode -> noise -> decode (majority)

Scenario B deliberately omits measure_syndrome() and correct(). If the
QBER of A is significantly lower than that of B, the syndrome correction
contributes something. If A ~ B, the reduction is explained by redundancy
and majority voting.

A third scenario without redundancy (n = 1) is included as a reference,
which separates the effect of "repeating the qubit" from that of
"correcting the qubit".

Usage
-----
    python control_experiment/control_experiment.py                  # defaults
    python control_experiment/control_experiment.py 5000 0.15 3 2026 # explicit

The script does NOT write or modify files: it only prints to the screen.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

# Make the repository root importable when the script is run from any directory.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np

# ---------------------------------------------------------------------------
# Imports: compatible with the English reproducible package in the remote
# repository (src/qec.py with `encode`, src/simulation.py, src/channel.py)
# and with the Spanish working tree (src/qec.py with `codificar`,
# src/simulacion.py, src/canal.py). The underlying physics is identical.
# ---------------------------------------------------------------------------
try:
    from src.qec import encode, measure_syndrome, correct, decode
    from src.simulation import depolarizing_channel_n
    from src.channel import depolarizing_channel
    from src.bb84 import prepare_qubit, measure_qubit
except ImportError:  # Spanish module/function names (local working tree)
    from src.qec import (
        codificar as encode,
        medir_sindrome as measure_syndrome,
        corregir as correct,
        decodificar as decode,
    )
    from src.simulacion import canal_depolarizante_n as depolarizing_channel_n
    from src.canal import canal_depolarizante as depolarizing_channel
    from src.bb84 import preparar_qubit as prepare_qubit
    from src.bb84 import medir_qubit as measure_qubit


# ===========================================================================
# Default parameters
# ===========================================================================

N_QUBITS = 3        # repetition-code size (n)
NOISE_P = 0.15      # error probability per physical qubit (p)
N_ITER = 2000       # iterations (logical bits) per scenario
SEED = 2026         # base seed


# ===========================================================================
# Utilities
# ===========================================================================

def _qber_with_standard_error(errors: int, total: int) -> tuple[float, float]:
    """Return (QBER, binomial standard error)."""
    qber = errors / total
    if 0.0 < qber < 1.0:
        se = float(np.sqrt(qber * (1.0 - qber) / total))
    else:
        se = 0.0
    return qber, se


# ===========================================================================
# Scenario A: QEC pipeline (syndrome + correction)
# ===========================================================================

def scenario_with_qec(n_iter: int, n: int, p: float, seed: int) -> dict:
    """
    Scenario A: encode -> channel -> measure_syndrome -> correct -> decode.

    The original project logic is not modified: the functions from
    src.qec and src.simulation are used exactly as implemented.
    """
    np.random.seed(seed)

    errors = 0
    non_trivial_syndromes = 0
    effective_corrections = 0

    for _ in range(n_iter):
        bit = int(np.random.randint(0, 2))

        # 1) Encoding: |b> -> |bbb>
        rho = encode(bit, n)

        # 2) Noisy channel, independent per physical qubit
        rho_err = depolarizing_channel_n(rho, p, n)

        # 3) Syndrome measurement
        syndrome = measure_syndrome(rho_err, n)
        if any(s != 0 for s in syndrome):
            non_trivial_syndromes += 1

        # 4) Correction
        rho_dec = correct(rho_err, syndrome, n)
        if not np.allclose(rho_dec.full(), rho_err.full(), atol=1e-12):
            effective_corrections += 1

        # 5) Majority-vote decoding
        bob_bit = decode(rho_dec, n)

        if bob_bit != bit:
            errors += 1

    qber, se = _qber_with_standard_error(errors, n_iter)
    return {
        "qber": qber,
        "se": se,
        "errors": errors,
        "n_iter": n_iter,
        "non_trivial_syndromes": non_trivial_syndromes,
        "effective_corrections": effective_corrections,
    }


# ===========================================================================
# Scenario B: redundancy only (no measure_syndrome, no correct)
# ===========================================================================

def scenario_redundancy_only(n_iter: int, n: int, p: float, seed: int) -> dict:
    """
    Scenario B: encode -> channel -> decode.

    QEC is omitted entirely: the noisy state goes directly to decode(),
    which performs majority voting. This simulates "classical redundancy
    only".
    """
    np.random.seed(seed)

    errors = 0

    for _ in range(n_iter):
        bit = int(np.random.randint(0, 2))

        rho = encode(bit, n)
        rho_err = depolarizing_channel_n(rho, p, n)

        # No syndrome and no correction: the noisy state goes straight through.
        bob_bit = decode(rho_err, n)

        if bob_bit != bit:
            errors += 1

    qber, se = _qber_with_standard_error(errors, n_iter)
    return {
        "qber": qber,
        "se": se,
        "errors": errors,
        "n_iter": n_iter,
    }


# ===========================================================================
# Reference scenario: no redundancy (n = 1)
# ===========================================================================

def scenario_without_redundancy(n_iter: int, p: float, seed: int) -> dict:
    """
    Reference: a single qubit in the Z basis, with no repetition or
    majority vote. It measures the QBER before any redundancy.
    """
    np.random.seed(seed)

    errors = 0

    for _ in range(n_iter):
        bit = int(np.random.randint(0, 2))

        rho = prepare_qubit(bit, 0)              # Z basis
        rho_err = depolarizing_channel(rho, p)
        bob_bit = measure_qubit(rho_err, 0)      # Z basis

        if bob_bit != bit:
            errors += 1

    qber, se = _qber_with_standard_error(errors, n_iter)
    return {
        "qber": qber,
        "se": se,
        "errors": errors,
        "n_iter": n_iter,
    }


# ===========================================================================
# Results presentation
# ===========================================================================

def main() -> None:
    # Force UTF-8 on the Windows console when possible.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    n_iter = int(sys.argv[1]) if len(sys.argv) > 1 else N_ITER
    p = float(sys.argv[2]) if len(sys.argv) > 2 else NOISE_P
    n = int(sys.argv[3]) if len(sys.argv) > 3 else N_QUBITS
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else SEED

    if n < 3 or n % 2 == 0:
        raise SystemExit("ERROR: n must be odd and >= 3.")
    if not (0.0 <= p <= 1.0):
        raise SystemExit("ERROR: p must be in [0, 1].")
    if n_iter < 1:
        raise SystemExit("ERROR: the number of iterations must be >= 1.")

    print("=" * 80)
    print(" CONTROL EXPERIMENT - QEC or classical redundancy only?")
    print("=" * 80)
    print(f" Code size (n) .................... {n} qubits")
    print(f" Noise per qubit (p) .............. {p:.4f}")
    print(f" Iterations per scenario .......... {n_iter}")
    print(f" Channel .......................... depolarizing, independent per qubit")
    print(f" Seeds (A, B, R) .................. {seed}, {seed + 1}, {seed + 2}")
    print("-" * 80)
    print(" A) With QEC ........ encode -> noise -> syndrome -> correct -> decode")
    print(" B) Redundancy only . encode -> noise -> (no correction)       -> decode")
    print(" R) Reference ....... 1 qubit, no redundancy and no majority vote")
    print("=" * 80)

    res_a = scenario_with_qec(n_iter, n, p, seed)
    res_b = scenario_redundancy_only(n_iter, n, p, seed + 1)
    res_r = scenario_without_redundancy(n_iter, p, seed + 2)

    difference = res_a["qber"] - res_b["qber"]
    se_difference = float(np.hypot(res_a["se"], res_b["se"]))
    z = difference / se_difference if se_difference > 0 else 0.0

    # ------------------------------------------------------------------
    # Table 1: requested comparison
    # ------------------------------------------------------------------
    print()
    print("[1] QBER COMPARISON TABLE")
    print("-" * 80)
    print(f" {'Scenario':<44} {'QBER':>8} {'SE':>8} {'Errors':>10}")
    print("-" * 80)
    print(f" {'A) With QEC (syndrome + correction)':<44} "
          f"{res_a['qber']:>8.4f} {res_a['se']:>8.4f} "
          f"{res_a['errors']:>5}/{res_a['n_iter']:<4}")
    print(f" {'B) Redundancy only (no correction)':<44} "
          f"{res_b['qber']:>8.4f} {res_b['se']:>8.4f} "
          f"{res_b['errors']:>5}/{res_b['n_iter']:<4}")
    print("-" * 80)
    print(f" {'Difference (A - B)':<44} "
          f"{difference:>+8.4f} {se_difference:>8.4f}")
    print(f" {'z statistic = (A - B) / SE':<44} {z:>+8.2f}")
    print("-" * 80)

    # ------------------------------------------------------------------
    # Table 2: mechanism diagnostics
    # ------------------------------------------------------------------
    print()
    print("[2] MECHANISM DIAGNOSTICS (Scenario A)")
    print("-" * 80)
    frac_syn = res_a["non_trivial_syndromes"] / n_iter
    frac_corr = res_a["effective_corrections"] / n_iter
    print(f" Non-trivial syndrome (error detected) ... "
          f"{res_a['non_trivial_syndromes']:>5}/{n_iter}  ({frac_syn:6.2%})")
    print(f" Effective corrections applied ........... "
          f"{res_a['effective_corrections']:>5}/{n_iter}  ({frac_corr:6.2%})")
    print(" (If both are 0, 'correct' did not modify any state: A and B")
    print("  are the same channel as far as the decoded bit is concerned.)")

    # ------------------------------------------------------------------
    # Table 3: no-redundancy reference and theoretical values
    # ------------------------------------------------------------------
    q = 2.0 * p / 3.0
    qber_no_redundancy_theory = q
    qber_majority_theory = sum(
        math.comb(n, k) * q**k * (1.0 - q) ** (n - k)
        for k in range(n // 2 + 1, n + 1)
    )

    print()
    print("[3] REFERENCE: NO REDUNDANCY AND THEORETICAL VALUES")
    print("-" * 80)
    print(f" q = 2p/3 (effective bit-flip probability per qubit) ... {q:.4f}")
    print(f" {'Scenario':<44} {'QBER':>8} {'SE':>8} {'Errors':>10}")
    print("-" * 80)
    print(f" {'R) No redundancy (n=1)':<44} "
          f"{res_r['qber']:>8.4f} {res_r['se']:>8.4f} "
          f"{res_r['errors']:>5}/{res_r['n_iter']:<4}")
    print("-" * 80)
    print(f" Theoretical QBER without redundancy (1 qubit) ..... "
          f"{qber_no_redundancy_theory:.4f}")
    print(f" Theoretical QBER, majority of {n} (no QEC) ......... "
          f"{qber_majority_theory:.4f}")
    print(" (The second value is the probability that more than n/2")
    print(f"  of the {n} qubits flip.)")

    # ------------------------------------------------------------------
    # Automatic interpretation of the result
    # ------------------------------------------------------------------
    print()
    print("[4] INTERPRETATION OF THE RESULT")
    print("-" * 80)
    if abs(z) < 2.0:
        print(f" * The A - B difference ({difference:+.4f}) is NOT significant "
              f"(|z| = {abs(z):.2f} < 2).")
    else:
        print(f" * The A - B difference ({difference:+.4f}) is significant "
              f"(|z| = {abs(z):.2f} >= 2).")

    if res_a["effective_corrections"] == 0:
        print(" * correct() did not act in any iteration: the measured syndrome")
        print("   was trivial and the state reached the decoder intact.")
        print(" * Therefore, in this experiment the QBER reduction does NOT come")
        print("   from quantum correction, but from redundancy (n qubits) and")
        print("   from majority voting in decode().")
    else:
        print(f" * correct() acted in {res_a['effective_corrections']} iterations;")
        print("   part of the difference (if any) may be attributed to QEC.")

    print(" * Theoretical note: for the bit-flip repetition code, correcting")
    print("   a single error from the syndrome is operationally equivalent to")
    print("   majority voting. A QEC advantage appears with codes that correct")
    print("   both X and Z (e.g., Shor or surface codes), not with the")
    print("   repetition code in the Z basis.")
    print("=" * 80)


if __name__ == "__main__":
    main()
