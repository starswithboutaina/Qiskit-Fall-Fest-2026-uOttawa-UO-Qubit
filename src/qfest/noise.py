"""Configurable Aer noise models, aligned with the qfest-plots interface."""

from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, ReadoutError, depolarizing_error


def from_backend(backend):
    """Create an Aer simulator using a backend's noise characteristics."""
    return AerSimulator.from_backend(backend)


def simple_model(p1q=4e-4, p2q=3e-3, p_meas=3e-3):
    """Build depolarizing and readout noise for logical and IBM basis gates."""
    noise_model = NoiseModel()
    one_qubit_error = depolarizing_error(p1q, 1)
    two_qubit_error = depolarizing_error(p2q, 2)
    readout_error = ReadoutError([
        [1 - p_meas, p_meas],
        [p_meas, 1 - p_meas],
    ])

    noise_model.add_all_qubit_quantum_error(
        one_qubit_error, ["h", "x", "rx", "sx", "rz"]
    )
    noise_model.add_all_qubit_quantum_error(
        two_qubit_error, ["cx", "cz", "ecr"]
    )
    noise_model.add_all_qubit_readout_error(readout_error)
    return noise_model
