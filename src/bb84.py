"""
Module for simulating the BB84 protocol without error correction.

This module implements the steps of the BB84 protocol: preparation,
transmission over a depolarizing channel, measurement in a random
basis, sifting, and QBER calculation.
"""

import numpy as np
import qutip as qt

from src.channel import depolarizing_channel


def prepare_qubit(bit, basis):
    """
    Prepare a qubit in the given basis (Z or X) according to the given bit.

    Args:
        bit (int): 0 or 1.
        basis (int): 0 for the Z basis, 1 for the X basis.

    Returns:
        Qobj: Density matrix of the prepared qubit.
    """
    if basis == 0:  # Z basis
        if bit == 0:
            return qt.ket2dm(qt.basis(2, 0))  # |0>
        else:
            return qt.ket2dm(qt.basis(2, 1))  # |1>
    elif basis == 1:  # X basis
        ket_plus = (qt.basis(2, 0) + qt.basis(2, 1)).unit()   # |+>
        ket_minus = (qt.basis(2, 0) - qt.basis(2, 1)).unit()  # |->
        return qt.ket2dm(ket_plus if bit == 0 else ket_minus)
    else:
        raise ValueError("The basis must be 0 (Z) or 1 (X).")


def measure_qubit(rho, basis):
    """
    Measure the quantum state rho in the given basis and return the
    measured bit.

    Args:
        rho (Qobj): Density matrix of the qubit.
        basis (int): 0 for the Z basis, 1 for the X basis.

    Returns:
        int: Measured bit (0 or 1).
    """
    if basis == 0:  # Z basis
        ket0 = qt.basis(2, 0)
        ket1 = qt.basis(2, 1)
    elif basis == 1:  # X basis
        ket0 = (qt.basis(2, 0) + qt.basis(2, 1)).unit()   # |+>
        ket1 = (qt.basis(2, 0) - qt.basis(2, 1)).unit()   # |->
    else:
        raise ValueError("The basis must be 0 (Z) or 1 (X).")

    # Projectors
    proj_0 = ket0 * ket0.dag()
    proj_1 = ket1 * ket1.dag()

    # Probabilities: P(i) = Tr(rho * Pi)
    prob_0 = float((rho * proj_0).tr().real)
    prob_1 = float((rho * proj_1).tr().real)

    # Normalize (to compensate for numerical errors)
    total = prob_0 + prob_1
    prob_0 /= total
    prob_1 /= total

    # Sample the outcome
    result = np.random.choice([0, 1], p=[prob_0, prob_1])
    return int(result)


def simulate_bb84(N, p):
    """
    Simulate the BB84 protocol without error correction.

    Args:
        N (int): Number of transmitted qubits.
        p (float): Error probability of the depolarizing channel.

    Returns:
        tuple: (QBER, sifted_key_length, alice_bits, bob_bits)
    """
    # Alice generates N bits and N random bases
    alice_bits = np.random.randint(0, 2, size=N)
    alice_bases = np.random.randint(0, 2, size=N)

    # Bob chooses N random bases (independently of Alice)
    bob_bases = np.random.randint(0, 2, size=N)

    bob_bits = []

    # Qubit-by-qubit transmission
    for i in range(N):
        rho = prepare_qubit(alice_bits[i], alice_bases[i])
        rho_depol = depolarizing_channel(rho, p)
        bob_bit = measure_qubit(rho_depol, bob_bases[i])
        bob_bits.append(bob_bit)

    bob_bits = np.array(bob_bits)

    # Sifting: keep only the positions where the bases match
    matching_indices = np.where(alice_bases == bob_bases)[0]

    if len(matching_indices) == 0:
        return 0.0, 0, alice_bits, bob_bits

    alice_bits_sifted = alice_bits[matching_indices]
    bob_bits_sifted = bob_bits[matching_indices]

    # QBER
    discrepancies = np.sum(alice_bits_sifted != bob_bits_sifted)
    qber = discrepancies / len(matching_indices)

    return qber, len(matching_indices), alice_bits, bob_bits


# ==================== VALIDATION TEST ====================
if __name__ == "__main__":
    print("=" * 60)
    print("BB84 VALIDATION WITHOUT QEC")
    print("=" * 60)
    print(f"{'p':>6} | {'QBER sim':>10} | {'QBER theo':>10} | {'|delta|':>8}")
    print("-" * 60)

    N = 5000
    for p in [0.01, 0.05, 0.10, 0.15, 0.20, 0.25]:
        qber, key_length, _, _ = simulate_bb84(N, p)
        qber_theoretical = (2 / 3) * p
        delta = abs(qber - qber_theoretical)
        print(f"{p:>6.2f} | {qber:>10.4f} | {qber_theoretical:>10.4f} | {delta:>8.4f}")
    print("=" * 60)
