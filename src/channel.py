"""
Module for simulating noisy quantum channels.

This module implements the depolarizing channel, which is the standard
noise model for quantum error correction (QEC) analysis in QKD.
"""

import numpy as np
import qutip as qt


def depolarizing_channel(rho, p):
    """
    Apply the depolarizing channel to a quantum state.

    The depolarizing channel is defined as:
        E(rho) = (1 - p) rho + (p / 3) (X rho X + Y rho Y + Z rho Z)

    where p is the error probability and X, Y, Z are the Pauli
    operators.

    Args:
        rho (Qobj): Density matrix of the qubit (2x2 Qobj).
        p (float): Error probability, in [0, 1].

    Returns:
        Qobj: Density matrix after the depolarizing channel.
    """
    X = qt.sigmax()
    Y = qt.sigmay()
    Z = qt.sigmaz()

    # Each Pauli term acts on BOTH sides: O rho O-dagger
    rho_depol = (1 - p) * rho + (p / 3) * (X * rho * X + Y * rho * Y + Z * rho * Z)
    return rho_depol


def measurement_probabilities(rho):
    """
    Compute the probabilities of measuring |0> and |1> in the Z basis.

    Args:
        rho (Qobj): Density matrix.

    Returns:
        tuple: (P(0), P(1))
    """
    p0 = np.real(rho[0, 0])  # Diagonal element (0, 0)
    p1 = np.real(rho[1, 1])  # Diagonal element (1, 1)
    return p0, p1


def depolarizing_channel_n(rho, p, n):
    """
    Apply the depolarizing channel independently to each of the n
    qubits of a joint state.

    Args:
        rho (Qobj): Density matrix of n qubits.
        p (float): Error probability per qubit.
        n (int): Number of qubits.

    Returns:
        Qobj: Density matrix after the noise.
    """
    identity = qt.qeye(2)
    X = qt.sigmax()
    Y = qt.sigmay()
    Z = qt.sigmaz()

    # Apply the channel to each qubit separately
    rho_out = rho
    for i in range(n):
        # Build operators X_i, Y_i, Z_i that act only on qubit i
        X_i = qt.tensor([X if j == i else identity for j in range(n)])
        Y_i = qt.tensor([Y if j == i else identity for j in range(n)])
        Z_i = qt.tensor([Z if j == i else identity for j in range(n)])

        # Apply the depolarizing channel to qubit i
        rho_out = (1 - p) * rho_out + (p / 3) * (
            X_i * rho_out * X_i.dag()
            + Y_i * rho_out * Y_i.dag()
            + Z_i * rho_out * Z_i.dag()
        )

    return rho_out


# ==================== VALIDATION TEST ====================

if __name__ == "__main__":
    # Initial state |0>
    rho0 = qt.ket2dm(qt.basis(2, 0))

    # Apply the depolarizing channel with p = 0.1
    p = 0.1
    rho_final = depolarizing_channel(rho0, p)

    # Compute probabilities
    p0, p1 = measurement_probabilities(rho_final)

    # Theoretical values
    p0_theoretical = 1 - (2 / 3) * p
    p1_theoretical = (2 / 3) * p

    print(f"=== Depolarizing channel with p = {p} ===")
    print("Initial state: |0>")
    print("")
    print(f"Simulated:  P(0) = {p0:.6f}, P(1) = {p1:.6f}")
    print(f"Theoretical: P(0) = {p0_theoretical:.6f}, P(1) = {p1_theoretical:.6f}")
    print("")
    print("Final density matrix:")
    print(rho_final)
