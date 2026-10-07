<<<<<<< HEAD
"""Local noise models for TFIM simulation.

The upstream qfest-plots source was unavailable. ``simple_model`` therefore
uses the project's pre-existing 1%/3% depolarizing-noise demo parameters.
"""

from qiskit_aer.noise import NoiseModel, depolarizing_error


def simple_model() -> NoiseModel:
    """Return a nontrivial depolarizing model for common IBM basis gates."""
    model = NoiseModel()
    model.add_all_qubit_quantum_error(
        depolarizing_error(0.01, 1), ["id", "rz", "sx", "x", "h", "rx"]
    )
    model.add_all_qubit_quantum_error(
        depolarizing_error(0.03, 2), ["cx", "cz", "ecr", "rzz"]
    )
    return model


def from_backend(backend) -> NoiseModel:
    """Build an Aer noise model from a backend's calibrated properties."""
    from qiskit_aer import AerSimulator

    model = AerSimulator.from_backend(backend).options.noise_model
    if model is None or not model.to_dict().get("errors"):
        raise ValueError("backend did not provide a nontrivial noise model")
    return model
=======
<<<<<<< Updated upstream
"""Aer noise models.  (Owner: Toto)

TODO:
  - from_backend(backend): AerSimulator/NoiseModel.from_backend from a fake or real backend.
  - simple_model(p1q, p2q, p_meas): depolarizing + readout model for quick sweeps
    (the Iceberg paper's H1-2 values: p1q=4e-4, p2q=3e-3, p_meas=3e-3).
"""


def from_backend(backend):
    raise NotImplementedError


def simple_model(p1q=4e-4, p2q=3e-3, p_meas=3e-3):
    raise NotImplementedError
=======
<<<<<<< Updated upstream
"""Local noise models for TFIM simulation.

The upstream qfest-plots source was unavailable. ``simple_model`` therefore
uses the project's pre-existing 1%/3% depolarizing-noise demo parameters.
"""

from qiskit_aer.noise import NoiseModel, depolarizing_error


def simple_model() -> NoiseModel:
    """Return a nontrivial depolarizing model for common IBM basis gates."""
    model = NoiseModel()
    model.add_all_qubit_quantum_error(
        depolarizing_error(0.01, 1), ["id", "rz", "sx", "x", "h", "rx"]
    )
    model.add_all_qubit_quantum_error(
        depolarizing_error(0.03, 2), ["cx", "cz", "ecr", "rzz"]
    )
    return model


def from_backend(backend) -> NoiseModel:
    """Build an Aer noise model from a backend's calibrated properties."""
    from qiskit_aer import AerSimulator

    model = AerSimulator.from_backend(backend).options.noise_model
    if model is None or not model.to_dict().get("errors"):
        raise ValueError("backend did not provide a nontrivial noise model")
    return model
=======
<<<<<<< HEAD
"""Aer noise models.  (Owner: Toto)

Provides:
- from_backend(backend): build an Aer simulator from a fake or real backend
- simple_model(...): configurable depolarizing + readout noise model
"""

from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error, ReadoutError


def from_backend(backend):
    """
    Create an AerSimulator using the noise characteristics of a backend.
    """
    return AerSimulator.from_backend(backend)


def simple_model(p1q=4e-4, p2q=3e-3, p_meas=3e-3):
    """
    Create a simple configurable Aer noise model.

    Parameters
    ----------
    p1q : float
        One-qubit depolarizing error probability.
    p2q : float
        Two-qubit depolarizing error probability.
    p_meas : float
        Symmetric readout error probability.
    """

    noise_model = NoiseModel()

    one_qubit_error = depolarizing_error(p1q, 1)
    two_qubit_error = depolarizing_error(p2q, 2)

    readout_error = ReadoutError(
        [
            [1 - p_meas, p_meas],
            [p_meas, 1 - p_meas],
        ]
    )

    noise_model.add_all_qubit_quantum_error(
        one_qubit_error,
        ["h", "x", "rx"],
    )

    noise_model.add_all_qubit_quantum_error(
        two_qubit_error,
        ["cx"],
    )

    noise_model.add_all_qubit_readout_error(readout_error)

    return noise_model
=======
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
>>>>>>> 349ea6f23109a798f27a61036250bcc65e0566eb
>>>>>>> Stashed changes
>>>>>>> Stashed changes
>>>>>>> 32cf08330958050c0b1b6fe0319511cdf646cf23
