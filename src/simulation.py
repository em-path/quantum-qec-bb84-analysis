"""
Integrated simulation module: BB84 + QEC + secret-key rate analysis.

Complete pipeline:
    1. Alice generates N bits and N random bases.
    2. Each bit is encoded into n qubits (QEC).
    3. Each physical qubit passes through a depolarizing channel with
       probability p.
    4. The syndrome is measured, the error is corrected, and the state
       is decoded.
    5. Sifting: only bits with matching bases are kept.
    6. The QBER and the secret-key rate are computed.

References:
    - Shor & Preskill (2000) - secret-key rate formula
    - Nielsen & Chuang (2010) - QEC, repetition code
"""

import numpy as np
import pandas as pd

from src.channel import depolarizing_channel, depolarizing_channel_n
from src.bb84 import prepare_qubit, measure_qubit
from src.qec import encode, measure_syndrome, correct, decode


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def secret_key_rate(qber):
    """
    Compute the secret-key rate according to Shor-Preskill.

    R = 1 - 2 * H2(QBER)

    where H2 is the binary Shannon entropy.
    If R < 0, the communication is not secure.

    Args:
        qber (float): Quantum Bit Error Rate.

    Returns:
        float: Secret-key rate (>= 0).
    """
    if qber <= 0:
        return 1.0
    if qber >= 0.5:
        return 0.0
    h2 = -qber * np.log2(qber) - (1 - qber) * np.log2(1 - qber)
    rate = 1 - 2 * h2
    return max(0.0, rate)


# ============================================================
# MAIN SIMULATION
# ============================================================

def simulate_bb84_with_qec(N, p, n):
    """
    Simulate BB84 with the n-qubit repetition code.

    Note: 'p' is the error probability PER PHYSICAL QUBIT.
    Noise is applied independently to each of the n qubits.

    Args:
        N (int): Number of logical bits transmitted.
        p (float): Error probability per physical qubit.
        n (int): Code size (1, 3, 5, 7). n=1 means no QEC.

    Returns:
        dict with:
            - qber: QBER over the sifted bits
            - n_sifted: number of bits that survive sifting
            - gross_rate: 1 - 2 * H2(QBER)
            - effective_rate: gross_rate / n
    """
    # Alice generates N bits and N bases
    alice_bits = np.random.randint(0, 2, size=N)
    alice_bases = np.random.randint(0, 2, size=N)

    # Bob chooses N random bases
    bob_bases = np.random.randint(0, 2, size=N)

    bob_bits = []

    for i in range(N):
        bit = alice_bits[i]
        basis = alice_bases[i]

        if n == 1:
            # Without QEC: prepare, transmit, measure
            rho = prepare_qubit(bit, basis)
            rho_err = depolarizing_channel(rho, p)
            bob_bit = measure_qubit(rho_err, bob_bases[i])
        else:
            # With QEC: encode, transmit, measure the syndrome,
            # correct, and decode
            rho = encode(bit, n)
            rho_err = depolarizing_channel_n(rho, p, n)
            syndrome = measure_syndrome(rho_err, n)
            rho_corrected = correct(rho_err, syndrome, n)
            bob_bit = decode(rho_corrected, n)

        bob_bits.append(bob_bit)

    bob_bits = np.array(bob_bits)

    # Sifting: keep only the positions where the bases match
    matching_indices = np.where(alice_bases == bob_bases)[0]

    if len(matching_indices) == 0:
        return {"qber": 0.0, "n_sifted": 0,
                "gross_rate": 0.0, "effective_rate": 0.0}

    alice_bits_sifted = alice_bits[matching_indices]
    bob_bits_sifted = bob_bits[matching_indices]

    # QBER
    discrepancies = np.sum(alice_bits_sifted != bob_bits_sifted)
    qber = discrepancies / len(matching_indices)

    # Rates
    gross_rate = secret_key_rate(qber)
    effective_rate = gross_rate / n

    return {
        "qber": qber,
        "n_sifted": len(matching_indices),
        "gross_rate": gross_rate,
        "effective_rate": effective_rate,
    }


# ============================================================
# PARAMETER SWEEP
# ============================================================

def parameter_sweep(N=3000,
                    p_values=None,
                    n_values=None,
                    csv_path="data/final_results.csv"):
    """
    Run the simulation for multiple (p, n) pairs and save the results.

    Args:
        N (int): Number of bits per simulation.
        p_values (list): Values of p to sweep.
        n_values (list): Values of n (code sizes).
        csv_path (str): Path to the output CSV file.

    Returns:
        pd.DataFrame with columns: p, n, qber, n_sifted,
        gross_rate, effective_rate.
    """
    if p_values is None:
        p_values = [0.00, 0.02, 0.04, 0.06, 0.08, 0.10,
                    0.12, 0.14, 0.16, 0.18, 0.20,
                    0.22, 0.24, 0.26, 0.28, 0.30]
    if n_values is None:
        n_values = [1, 3, 5, 7]

    rows = []
    print("=" * 70)
    print(f"PARAMETER SWEEP (N={N} per combination)")
    print("=" * 70)
    print(f"{'p':>6} | {'n':>3} | {'QBER':>10} | {'n_sifted':>8} "
          f"| {'R_gross':>10} | {'R_eff':>10}")
    print("-" * 70)

    for p in p_values:
        for n in n_values:
            result = simulate_bb84_with_qec(N=N, p=p, n=n)
            rows.append({
                "p": p,
                "n": n,
                "qber": result["qber"],
                "n_sifted": result["n_sifted"],
                "gross_rate": result["gross_rate"],
                "effective_rate": result["effective_rate"],
            })
            print(f"{p:>6.2f} | {n:>3} | {result['qber']:>10.4f} "
                  f"| {result['n_sifted']:>8} "
                  f"| {result['gross_rate']:>10.4f} "
                  f"| {result['effective_rate']:>10.4f}")

    df = pd.DataFrame(rows)
    df.to_csv(csv_path, index=False)
    print("=" * 70)
    print(f"Results saved to: {csv_path}")

    return df


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    import os
    os.makedirs("data", exist_ok=True)
    parameter_sweep(N=3000)
