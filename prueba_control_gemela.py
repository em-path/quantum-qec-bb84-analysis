"""
prueba_control_gemela.py - Strict paired ("twin") control experiment
====================================================================

Question
--------
Compare the QBER with QEC enabled (Scenario A) and with QEC disabled
(Scenario B) using the exact same random configuration for both. The goal
is to isolate the effect of the syndrome-based correction: if the
correction does something, A and B must differ; if correction is a no-op,
A and B must be bit-for-bit identical.

Paired (twin) design
--------------------
For every iteration the two scenarios share:

    1. the same logical bit,
    2. the same encoded state,
    3. the same noisy state rho_err (the channel is deterministic),
    4. the same decoder random draws.

Point 4 is enforced by saving the NumPy RNG state before decoding A and
restoring it before decoding B. Both decoders therefore see the same
uniform random numbers. If the states passed to them are identical, the
decoded bits are identical by construction; if the correction changes the
state, the decoded bits may differ. This is the strongest possible paired
comparison.

Scenarios
---------
    A) With QEC ....... encode -> noise -> measure_syndrome ->
                        correct -> decode
    B) Without QEC .... encode -> noise -> decode

A reference scenario without redundancy (n = 1) is also reported.

Diagnostics (per iteration)
---------------------------
    - Did measure_syndrome() return a non-trivial syndrome?
    - Did correct() actually change the state?
    - Was the correction triggered (both conditions true)?
    - Did the decoded bits of A and B differ?
    - How many discordant pairs (b and c) are there?

Usage
-----
    python prueba_control_gemela.py
    python prueba_control_gemela.py 5000 0.15 3 2026

Arguments: iterations, p, n, seed. The script prints only; it does not
write or modify files.
"""

from __future__ import annotations

import math
import sys

import numpy as np

# ---------------------------------------------------------------------------
# Imports: English package (remote repo) first, Spanish tree (local) second.
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
N_ITER = 2000       # iterations (logical bits)
SEED = 2026         # single seed shared by both scenarios


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
# Paired (twin) experiment
# ===========================================================================

def run_paired_experiment(n_iter: int, n: int, p: float, seed: int) -> dict:
    """
    Run Scenarios A and B on the same random configuration.

    For each iteration, the bit, the noisy state, and the decoder random
    draws are shared. The only difference is the state passed to decode():
    the corrected state in A, the noisy state in B.

    Returns a dictionary with QBERs, counts, and paired discordances.
    """
    np.random.seed(seed)

    errors_a = 0
    errors_b = 0

    non_trivial_syndromes = 0
    corrections_applied = 0
    correction_triggered = 0
    syndrome_but_unchanged = 0
    changed_without_syndrome = 0
    different_decoded_bits = 0

    # Discordant pairs for the paired analysis:
    #   b = A correct, B wrong
    #   c = A wrong, B correct
    b_discordant = 0
    c_discordant = 0

    for _ in range(n_iter):
        bit = int(np.random.randint(0, 2))

        # Shared encoded state and shared noisy state
        rho = encode(bit, n)
        rho_err = depolarizing_channel_n(rho, p, n)

        # --- Scenario A: syndrome measurement + correction -----------------
        syndrome = measure_syndrome(rho_err, n)
        non_trivial = any(s != 0 for s in syndrome)
        if non_trivial:
            non_trivial_syndromes += 1

        rho_corrected = correct(rho_err, syndrome, n)
        changed = not np.allclose(
            rho_corrected.full(), rho_err.full(), atol=1e-12
        )
        if changed:
            corrections_applied += 1

        if non_trivial and changed:
            correction_triggered += 1
        elif non_trivial and not changed:
            syndrome_but_unchanged += 1
        elif not non_trivial and changed:
            changed_without_syndrome += 1

        # --- Paired decoding: identical random draws for A and B -----------
        rng_state_before_decode = np.random.get_state()
        bit_a = decode(rho_corrected, n)
        np.random.set_state(rng_state_before_decode)
        bit_b = decode(rho_err, n)

        err_a = int(bit_a != bit)
        err_b = int(bit_b != bit)
        errors_a += err_a
        errors_b += err_b

        if bit_a != bit_b:
            different_decoded_bits += 1
        if err_a == 0 and err_b == 1:
            b_discordant += 1
        elif err_a == 1 and err_b == 0:
            c_discordant += 1

    qber_a, se_a = _qber_with_standard_error(errors_a, n_iter)
    qber_b, se_b = _qber_with_standard_error(errors_b, n_iter)

    difference = qber_a - qber_b
    paired_se = math.sqrt(b_discordant + c_discordant) / n_iter
    if b_discordant + c_discordant > 0:
        paired_z = (c_discordant - b_discordant) / math.sqrt(
            b_discordant + c_discordant
        )
    else:
        paired_z = 0.0

    return {
        "qber_a": qber_a,
        "se_a": se_a,
        "errors_a": errors_a,
        "qber_b": qber_b,
        "se_b": se_b,
        "errors_b": errors_b,
        "difference": difference,
        "paired_se": paired_se,
        "paired_z": paired_z,
        "b_discordant": b_discordant,
        "c_discordant": c_discordant,
        "n_iter": n_iter,
        "non_trivial_syndromes": non_trivial_syndromes,
        "corrections_applied": corrections_applied,
        "correction_triggered": correction_triggered,
        "syndrome_but_unchanged": syndrome_but_unchanged,
        "changed_without_syndrome": changed_without_syndrome,
        "different_decoded_bits": different_decoded_bits,
    }


# ===========================================================================
# Reference: no redundancy (n = 1)
# ===========================================================================

def run_no_redundancy_reference(n_iter: int, p: float, seed: int) -> dict:
    """Single qubit in the Z basis, with no repetition or majority vote."""
    np.random.seed(seed)

    errors = 0
    for _ in range(n_iter):
        bit = int(np.random.randint(0, 2))
        rho = prepare_qubit(bit, 0)
        rho_err = depolarizing_channel(rho, p)
        bob_bit = measure_qubit(rho_err, 0)
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

    print("=" * 82)
    print(" STRICT PAIRED (TWIN) CONTROL EXPERIMENT")
    print("=" * 82)
    print(f" Code size (n) .................... {n} qubits")
    print(f" Noise per qubit (p) .............. {p:.4f}")
    print(f" Iterations ....................... {n_iter}")
    print(f" Shared seed (A and B) ............ {seed}")
    print(f" Reference seed (R) ............... {seed + 2}")
    print(" Pairing .......................... same bits, same noisy state,")
    print("                                    same decoder random draws")
    print("-" * 82)
    print(" A) With QEC ....... encode -> noise -> syndrome -> correct -> decode")
    print(" B) Without QEC .... encode -> noise -> decode")
    print("=" * 82)

    res = run_paired_experiment(n_iter, n, p, seed)
    ref = run_no_redundancy_reference(n_iter, p, seed + 2)

    # ------------------------------------------------------------------
    # Table 1: paired QBER comparison
    # ------------------------------------------------------------------
    print()
    print("[1] PAIRED QBER COMPARISON")
    print("-" * 82)
    print(f" {'Scenario':<46} {'QBER':>8} {'SE':>8} {'Errors':>11}")
    print("-" * 82)
    print(f" {'A) With QEC (syndrome + correction)':<46} "
          f"{res['qber_a']:>8.4f} {res['se_a']:>8.4f} "
          f"{res['errors_a']:>5}/{res['n_iter']:<5}")
    print(f" {'B) Without QEC (redundancy only)':<46} "
          f"{res['qber_b']:>8.4f} {res['se_b']:>8.4f} "
          f"{res['errors_b']:>5}/{res['n_iter']:<5}")
    print("-" * 82)
    print(f" {'Difference (A - B)':<46} {res['difference']:>+8.4f} "
          f"{res['paired_se']:>8.4f}")
    print(f" {'Discordant pairs b (A correct, B wrong)':<46} "
          f"{res['b_discordant']:>8d}")
    print(f" {'Discordant pairs c (A wrong, B correct)':<46} "
          f"{res['c_discordant']:>8d}")
    print(f" {'Paired McNemar-style z = (c - b)/sqrt(b + c)':<46} "
          f"{res['paired_z']:>+8.2f}")
    print("-" * 82)

    # ------------------------------------------------------------------
    # Table 2: per-iteration correction diagnostics
    # ------------------------------------------------------------------
    print()
    print("[2] CORRECTION DIAGNOSTICS (PER ITERATION)")
    print("-" * 82)
    print(f" {'Non-trivial syndromes (error detected)':<46} "
          f"{res['non_trivial_syndromes']:>5}/{n_iter}  "
          f"({res['non_trivial_syndromes'] / n_iter:6.2%})")
    print(f" {'Corrections that changed the state':<46} "
          f"{res['corrections_applied']:>5}/{n_iter}  "
          f"({res['corrections_applied'] / n_iter:6.2%})")
    print(f" {'Correction triggered (both conditions)':<46} "
          f"{res['correction_triggered']:>5}/{n_iter}  "
          f"({res['correction_triggered'] / n_iter:6.2%})")
    print("-" * 82)
    print(f" {'Syndrome non-trivial but state unchanged':<46} "
          f"{res['syndrome_but_unchanged']:>5}/{n_iter}")
    print(f" {'State changed without non-trivial syndrome':<46} "
          f"{res['changed_without_syndrome']:>5}/{n_iter}")
    print(f" {'Decoded bits differing between A and B':<46} "
          f"{res['different_decoded_bits']:>5}/{n_iter}")

    # ------------------------------------------------------------------
    # Table 3: no-redundancy reference and theory
    # ------------------------------------------------------------------
    q = 2.0 * p / 3.0
    qber_majority_theory = sum(
        math.comb(n, k) * q**k * (1.0 - q) ** (n - k)
        for k in range(n // 2 + 1, n + 1)
    )

    print()
    print("[3] NO-REDUNDANCY REFERENCE AND THEORETICAL VALUES")
    print("-" * 82)
    print(f" q = 2p/3 (effective bit-flip probability per qubit) ... {q:.4f}")
    print(f" {'R) No redundancy (n = 1)':<46} "
          f"{ref['qber']:>8.4f} {ref['se']:>8.4f} "
          f"{ref['errors']:>5}/{ref['n_iter']:<5}")
    print(f" {'Theoretical QBER without redundancy (1 qubit)':<46} "
          f"{q:>8.4f}")
    print(f" {'Theoretical QBER, majority of n (no QEC)':<46} "
          f"{qber_majority_theory:>8.4f}")
    print(" (The majority value is the probability that more than n/2")
    print(f"  of the {n} qubits flip. For n = 3 it is 3q^2(1-q) + q^3.)")

    # ------------------------------------------------------------------
    # Automatic interpretation
    # ------------------------------------------------------------------
    print()
    print("[4] INTERPRETATION OF THE PAIRED RESULT")
    print("-" * 82)

    if res["correction_triggered"] == 0:
        print(" * No correction was triggered in any iteration: the syndrome")
        print("   was trivial and correct() left the state unchanged.")
        print(f" * Consequently, A and B are the same stochastic channel:")
        print(f"   QBER_A = QBER_B = {res['qber_a']:.4f}, with "
              f"{res['different_decoded_bits']} differing decoded bits.")
        print(" * This paired experiment does NOT show a correction effect.")
        print("   The QBER reduction is produced by redundancy (n qubits)")
        print("   and majority voting, not by the syndrome step.")
    elif res["qber_a"] < res["qber_b"]:
        print(f" * Correction was triggered {res['correction_triggered']} times")
        print(f"   and QBER_A ({res['qber_a']:.4f}) < QBER_B "
              f"({res['qber_b']:.4f}): the correction contributed.")
    else:
        print(f" * Correction was triggered {res['correction_triggered']} times,")
        print(f"   but QBER_A ({res['qber_a']:.4f}) is not better than QBER_B "
              f"({res['qber_b']:.4f}).")
        print("   This is consistent with the equivalence between single-error")
        print("   syndrome correction and majority voting for this code.")

    print(" * Implementation note: measure_syndrome() uses the expectation")
    print("   value <Z_i Z_{i+1}> instead of a projective measurement. For the")
    print("   depolarized product state, <Z_i Z_{i+1}> = (1 - 2q)^2 = "
          f"{(1 - 2 * q) ** 2:.4f} > 0,")
    print("   so the syndrome is trivial for p < 0.75 and correct() never")
    print("   fires. Even with a true projective syndrome, single-error")
    print("   correction would be equivalent to majority voting for this code.")
    print("=" * 82)


if __name__ == "__main__":
    main()
