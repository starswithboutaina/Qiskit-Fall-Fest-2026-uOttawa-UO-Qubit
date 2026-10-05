import numpy as np

from qfest.ed import quench
from qfest.results import save


# Parameters for the ED reference data
system_sizes = [6, 8, 10, 12]
fields = [0.5, 1.0, 2.0]

# Times from 0 to 20 in steps of 0.05
times = np.arange(0.0, 20.0 + 0.05, 0.05)


for n in system_sizes:
    for h in fields:

        print(f"Generating ED reference: N={n}, h={h}")

        result = quench(
            n=n,
            times=times,
            J=1.0,
            h=h,
            periodic=True
        )

        record = {
            "experiment": "ed_reference",
            "backend": "ed",
            "params": {
                "n": n,
                "J": 1.0,
                "h": h,
                "periodic": True
            },
            "method": "ed",
            "t": result["t"],
            "observables": {
                "Mz": result["Mz"],
                "Mx": result["Mx"],
                "Mzz": result["Mzz"]
            },
            "extra": {
                "num_times": len(times),
                "dt": 0.05
            }
        }

        filename = f"ed_n{n}_h{str(h).replace('.', 'p')}"

        path = save(record, filename)

        print(f"Saved: {path}")


print("\nDone! All ED reference files have been generated.")