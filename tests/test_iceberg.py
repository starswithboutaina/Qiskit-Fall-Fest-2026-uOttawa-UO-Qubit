import numpy as np
import pytest
from qiskit import ClassicalRegister, QuantumRegister
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator

from qfest.iceberg import decode_counts, encode_tfim, initialisation, syndrome_round
from qfest.tfim import tfim_circuit


@pytest.mark.parametrize("k", [2, 4, 6])
def test_initialisation_is_ghz(k):
    expected = np.zeros(2 ** (k + 2))
    expected[0] = expected[-1] = 2 ** -0.5
    assert np.allclose(Statevector(initialisation(k)).data, expected)


@pytest.mark.parametrize("k", [0, 3, 5])
def test_initialisation_rejects_bad_k(k):
    with pytest.raises(ValueError):
        initialisation(k)


@pytest.mark.parametrize("k,h", [(4, 0.5), (6, 2.0)])
def test_encoded_circuit_matches_tfim(k, h):
    """Noiseless: decoded magnet probabilities equal tfim_circuit's and nothing is discarded."""
    qc = encode_tfim(k, 1.0, h, 0.1, 10).remove_final_measurements(inplace=False)
    probs = Statevector(qc).probabilities()
    counts = {format(x, f"0{k + 2}b"): p for x, p in enumerate(probs) if p > 1e-12}
    kept, discard = decode_counts(counts, k)
    assert discard == pytest.approx(0.0, abs=1e-12)
    for magnets, p in Statevector(tfim_circuit(k, 1.0, h, 0.1, 10)).probabilities_dict().items():
        assert kept.get(magnets, 0.0) == pytest.approx(p, abs=1e-9)


@pytest.mark.parametrize("mistake,result", [(None, "00"), ("x", "01"), ("z", "10")])
def test_checkpoint_flags_the_right_mistake(mistake, result):
    k = 4
    qc = initialisation(k)
    qc.add_register(QuantumRegister(2, "a"))
    checks = ClassicalRegister(2, "checks")
    qc.add_register(checks)
    if mistake == "x":
        qc.x(0)
    if mistake == "z":
        qc.z(0)
    syndrome_round(qc, k, checks, 0)
    counts = AerSimulator(seed_simulator=1).run(qc, shots=200).result().get_counts()
    assert counts == {result: 200}


@pytest.mark.parametrize("rounds", [1, 2])
def test_checkpoints_never_fire_without_noise(rounds):
    qc = encode_tfim(4, 1.0, 1.0, 0.1, 10, rounds)
    counts = AerSimulator(seed_simulator=2).run(qc, shots=500).result().get_counts()
    assert decode_counts(counts, 4)[1] == 0.0


def test_decode_counts_example():
    kept, discard = decode_counts({"0000": 3500, "1111": 3480, "0101": 500, "0001": 20}, 2)
    assert kept == {"00": 6980, "01": 500}
    assert discard == pytest.approx(20 / 7500)


def test_decode_counts_drops_checkpoint_alarms():
    kept, discard = decode_counts({"0000 00": 90, "0000 01": 10}, 2)
    assert kept == {"00": 90}
    assert discard == pytest.approx(0.1)
