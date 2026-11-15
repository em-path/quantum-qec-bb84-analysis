"""
Module for quantum error correction (QEC).

Implements the n-qubit repetition code (n odd: 3, 5, 7), which corrects
bit-flip (X) errors through majority voting and syndrome measurement.

References:
    - Nielsen & Chuang (2010), Quantum Computation and Quantum Information
    - Gottesman (1997), Stabilizer codes and quantum error correction
"""

import numpy as np
import qutip as qt


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def _pauli_operator_n(n, operator, index):
    """
    Build the Pauli `operator` (X, Y, or Z) acting on qubit `index`
    of an n-qubit system.

    Args:
        n (int): Total number of qubits.
        operator (Qobj): Pauli operator (qt.sigmax(), qt.sigmay(), qt.sigmaz()).
        index (int): Position of the qubit on which the operator acts (0-indexed).

    Returns:
        Qobj: Tensor product operator over n qubits.
    """
    identity = qt.qeye(2)
    operators = [identity] * n
    operators[index] = operator
    return qt.tensor(operators)


# ============================================================
# 1. ENCODING
# ============================================================

def encode(bit, n):
    """
    Encode a logical bit into n physical qubits using the repetition
    code.

    |0>_L = |00...0>
    |1>_L = |11...1>

    Args:
        bit (int): Logical bit (0 or 1).
        n (int): Number of physical qubits (odd: 3, 5, 7).

    Returns:
        Qobj: Density matrix of the encoded state (n qubits).
    """
    if bit not in (0, 1):
        raise ValueError("The bit must be 0 or 1.")
    if n < 3 or n % 2 == 0:
        raise ValueError("n must be odd and >= 3.")

    ket = qt.basis(2, bit)
    state = qt.tensor([ket] * n)
    return qt.ket2dm(state)


# ============================================================
# 2. SYNDROME MEASUREMENT
# ============================================================

def measure_syndrome(rho, n):
    """
    Measure the syndromes of the repetition code.

    The stabilizer generators are:
        g_i = Z_i Z_{i+1},  for i = 0, ..., n-2

    Each measurement returns 0 (eigenvalue +1, no local error) or
    1 (eigenvalue -1, error detected).

    Args:
        rho (Qobj): Density matrix of the encoded state (n qubits).
        n (int): Number of qubits.

    Returns:
        tuple: (n-1)-bit syndrome, e.g. (0, 0) for n=3.
    """
    Z = qt.sigmaz()
    syndrome = []

    for i in range(n - 1):
        # g_i = Z_i * Z_{i+1}
        Zi = _pauli_operator_n(n, Z, i)
        Zi_next = _pauli_operator_n(n, Z, i + 1)
        g_i = Zi * Zi_next

        # Expectation value <g_i> = Tr(rho * g_i)
        value = float((rho * g_i).tr().real)

        # Syndrome: 0 if eigenvalue +1, 1 if eigenvalue -1
        syndrome.append(0 if value > 0 else 1)

    return tuple(syndrome)


# ============================================================
# 3. CORRECTION
# ============================================================

def correct(rho, syndrome, n):
    """
    Apply the correction indicated by the measured syndrome.

    For n=3, the correction table is:
        (0, 0) -> no error
        (1, 0) -> X on qubit 1
        (1, 1) -> X on qubit 2
        (0, 1) -> X on qubit 3

    Generalization: the (n-1)-bit syndrome indicates the position of
    the error. The syndrome pattern is a "binary code" that identifies
    the affected qubit.

    Args:
        rho (Qobj): Noisy density matrix.
        syndrome (tuple): (n-1)-bit syndrome.
        n (int): Number of qubits.

    Returns:
        Qobj: Corrected density matrix.
    """
    if all(s == 0 for s in syndrome):
        return rho  # No error

    # Determine the affected qubit from the syndrome
    error_qubit = _decode_syndrome(syndrome, n)

    if error_qubit is None:
        return rho  # Unrecognized syndrome: do not correct

    # Apply X to the affected qubit
    X = qt.sigmax()
    X_i = _pauli_operator_n(n, X, error_qubit)
    rho_corrected = X_i * rho * X_i.dag()

    return rho_corrected


def _decode_syndrome(syndrome, n):
    """
    Given an (n-1)-bit syndrome, identify the index of the qubit
    with an error.

    For the repetition code:
    - Error on qubit 0 -> syndrome (1, 0, 0, ..., 0)
    - Error on qubit 1 -> syndrome (1, 1, 0, ..., 0)
    - ...
    - Error on qubit k -> syndrome with ones in positions 0..k-1
    - Error on qubit n-1 -> syndrome (0, 0, ..., 0, 1)

    Args:
        syndrome (tuple): (n-1)-bit syndrome.
        n (int): Number of qubits.

    Returns:
        int or None: Index of the qubit with an error, or None if
        unrecognized.
    """
    s = list(syndrome)

    # Look for the corresponding pattern
    for qubit in range(n):
        # Build the expected syndrome for an error on `qubit`
        expected = [0] * (n - 1)
        if qubit < n - 1:
            for j in range(qubit + 1):
                expected[j] = 1
        else:
            expected[n - 2] = 1

        if s == expected:
            return qubit

    return None


# ============================================================
# 4. DECODING
# ============================================================

def decode(rho, n):
    """
    Decode the state by correcting through majority voting.

    Measure each qubit in the Z basis and return the majority bit.

    Args:
        rho (Qobj): Density matrix of the encoded state.
        n (int): Number of qubits.

    Returns:
        int: Decoded bit (0 or 1).
    """
    measured_bits = []

    for i in range(n):
        # Projector onto |0> on qubit i
        proj0_i = _pauli_operator_n(n, qt.ket2dm(qt.basis(2, 0)), i)
        proj1_i = _pauli_operator_n(n, qt.ket2dm(qt.basis(2, 1)), i)

        p0 = float((rho * proj0_i).tr().real)
        p1 = float((rho * proj1_i).tr().real)

        total = p0 + p1
        if total > 0:
            p0 /= total
            p1 /= total

        bit = 0 if np.random.random() < p0 else 1
        measured_bits.append(bit)

    # Majority voting
    return 1 if sum(measured_bits) > n // 2 else 0


# ============================================================
# UNIT TESTS
# ============================================================

def test_encoding():
    """An encoded bit must be measured correctly without noise."""
    for n in [3, 5, 7]:
        for bit in [0, 1]:
            rho = encode(bit, n)
            decoded_bit = decode(rho, n)
            assert decoded_bit == bit, \
                f"Failure: bit={bit}, n={n}, decoded={decoded_bit}"
    print("PASSED: test_encoding")


def test_syndrome_without_error():
    """Without noise, the syndrome must be all zeros."""
    for n in [3, 5, 7]:
        rho = encode(0, n)
        s = measure_syndrome(rho, n)
        assert all(b == 0 for b in s), \
            f"Failure: n={n}, syndrome={s}"
    print("PASSED: test_syndrome_without_error")


def test_syndrome_with_error():
    """With an X error on one qubit, the syndrome must detect it."""
    for n in [3, 5, 7]:
        for qubit in range(n):
            rho = encode(0, n)
            # Apply X to the qubit
            X_i = _pauli_operator_n(n, qt.sigmax(), qubit)
            rho_err = X_i * rho * X_i.dag()

            s = measure_syndrome(rho_err, n)
            # The syndrome must not be all zeros
            assert any(b == 1 for b in s), \
                f"Failure: n={n}, qubit={qubit}, syndrome={s}"

            # The correction must recover the state
            rho_corrected = correct(rho_err, s, n)
            bit = decode(rho_corrected, n)
            assert bit == 0, \
                f"Failure: n={n}, qubit={qubit}, decoded bit={bit}"
    print("PASSED: test_syndrome_with_error")


def test_qber_without_noise():
    """Without noise, the QBER must be 0."""
    for n in [3, 5, 7]:
        for bit in [0, 1]:
            rho = encode(bit, n)
            decoded_bit = decode(rho, n)
            assert decoded_bit == bit
    print("PASSED: test_qber_without_noise")


def test_qber_at_maximum_noise():
    """With extreme noise (very high p), the decoded bit must be nearly random."""
    from src.channel import depolarizing_channel_n
    n = 3
    p = 0.9
    successes = 0
    trials = 100
    for _ in range(trials):
        rho = encode(0, n)
        rho_err = depolarizing_channel_n(rho, p, n)
        s = measure_syndrome(rho_err, n)
        rho_corrected = correct(rho_err, s, n)
        bit = decode(rho_corrected, n)
        if bit == 0:
            successes += 1
    ratio = successes / trials
    assert 0.3 < ratio < 0.7, \
        f"Failure: success ratio = {ratio:.3f}"
    print(f"PASSED: test_qber_at_maximum_noise (ratio = {ratio:.3f})")


if __name__ == "__main__":
    print("=" * 60)
    print("QEC UNIT TESTS")
    print("=" * 60)
    test_encoding()
    test_syndrome_without_error()
    test_syndrome_with_error()
    test_qber_without_noise()
    test_qber_at_maximum_noise()
    print("=" * 60)
    print("All tests passed.")
