"""Iceberg cost-benefit sweep: does the [[k+2, k, 2]] watchdog beat plain Trotter under noise?

N = 6 and 8 periodic chains (6 = canonical size, 8 = Iceberg size), quench from |0...0>, dt = 0.1,
steps 5..40 (t = 0.5..4.0), h/J in {0.5, 1, 2}.
Variants: unprotected tfim_circuit, and encode_tfim with 0, 1, 2 checkpoints (syndrome rounds).
Noise: qfest.noise.simple_model (Toto), which puts two-qubit errors on cx only, so every circuit
is first converted to {cx, rz, rx, h, x}: each rzz/rxx becomes 2 noisy CNOTs, as on IBM hardware
(rz is virtual there, so it stays noiseless). All-to-all connectivity, so this is the best case
for Iceberg; heavy-hex SWAP overhead is analysed separately in hardware.py.
Error = |Mzz - Mzz_ED|. Run:  python experiments/iceberg_sweep.py
"""
import numpy as np
from qiskit import transpile
from qiskit_aer import AerSimulator

from qfest.ed import bonds, quench
from qfest.iceberg import decode_counts, encode_tfim
from qfest.noise import simple_model
from qfest.results import save
from qfest.tfim import tfim_circuit

SIZES = [6, 8]
J, DT, SHOTS = 1.0, 0.1, 20000
HS = [0.5, 1.0, 2.0]
STEPS = [5, 10, 15, 20, 25, 30, 35, 40]
ROUNDS = [0, 1, 2]
P1Q, P2Q, P_MEAS = 4e-4, 3e-3, 3e-3
BASIS = ["cx", "rz", "rx", "h", "x"]


def observables(counts, k):
    """Mz (RMS magnitude) and Mzz from magnet bitstrings (qubit 0 is the rightmost character)."""
    n = sum(counts.values())
    mz2 = mzz = 0.0
    for magnets, c in counts.items():
        s = [1 - 2 * int(ch) for ch in reversed(magnets)]
        mz2 += c * sum(s) ** 2
        mzz += c * sum(s[i] * s[j] for i, j in bonds(k))
    return float(np.sqrt(mz2 / n) / k), mzz / (n * k)


def cost(qc):
    return qc.count_ops().get("cx", 0), qc.depth()


def run_one(sim, k, h):
    times = [s * DT for s in STEPS]
    variants = ["plain"] + [f"r{r}" for r in ROUNDS]
    exact = quench(k, times, J, h)["Mzz"]
    rec = {v: {"Mz": [], "Mzz": [], "discard": [], "gates": [], "depth": []} for v in variants}
    for steps in STEPS:
        plain = tfim_circuit(k, J, h, DT, steps)
        plain.measure_all()
        circuits = {"plain": plain}
        for r in ROUNDS:
            circuits[f"r{r}"] = encode_tfim(k, J, h, DT, steps, r)
        for v, qc in circuits.items():
            qc = transpile(qc, basis_gates=BASIS, optimization_level=0)
            counts = sim.run(qc, shots=SHOTS).result().get_counts()
            kept, discard = (counts, 0.0) if v == "plain" else decode_counts(counts, k)
            mz, mzz = observables(kept, k)
            gates, depth = cost(qc)
            for key, val in zip(rec[v], (mz, mzz, discard, gates, depth)):
                rec[v][key].append(val)

    print(f"\nN = {k}, h/J = {h}: |Mzz error| x100 (discard %)")
    print("steps | plain | " + " | ".join(f"{r} checkpoints" for r in ROUNDS))
    for i, steps in enumerate(STEPS):
        cells = [f"{100 * abs(rec['plain']['Mzz'][i] - exact[i]):5.1f}"]
        for r in ROUNDS:
            d = rec[f"r{r}"]
            cells.append(f"{100 * abs(d['Mzz'][i] - exact[i]):5.1f} ({100 * d['discard'][i]:4.1f})")
        print(f"{steps:5d} | " + " | ".join(cells))

    for v in variants:
        d = rec[v]
        path = save({
            "experiment": "iceberg_sweep",
            "backend": "aer_noisy",
            "params": {"n": k, "J": J, "h": h, "dt": DT, "steps": STEPS, "periodic": True,
                       "rounds": None if v == "plain" else int(v[1:])},
            "method": "trotter_2nd" if v == "plain" else "iceberg",
            "t": times,
            "observables": {"Mz": d["Mz"], "Mzz": d["Mzz"]},
            "extra": {"shots": SHOTS, "discard_rate": d["discard"], "two_qubit_gates": d["gates"],
                      "depth": d["depth"], "Mzz_ed": exact,
                      "noise": {"p1q": P1Q, "p2q": P2Q, "p_meas": P_MEAS}},
        }, f"iceberg_sweep_n{k}_h{h}_{v}")
    print(f"saved {path.parent}/iceberg_sweep_n{k}_h{h}_*.json", flush=True)


def main():
    sim = AerSimulator(noise_model=simple_model(P1Q, P2Q, P_MEAS), seed_simulator=7)
    for k in SIZES:
        for h in HS:
            run_one(sim, k, h)


main()
