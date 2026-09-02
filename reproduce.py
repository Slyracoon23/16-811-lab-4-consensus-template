"""Predict the rate, then measure it, and write results.json."""

from __future__ import annotations

import argparse
import json

import numpy as np

import baselines
from evaluate import decay_rate, simulate
from method import ASSUMPTIONS, algebraic_connectivity, laplacian
from synthetic import EXACT, complete, path, ring, star

FAMILIES = {"complete": complete, "star": star, "ring": ring, "path": path}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=int, default=5)
    parser.add_argument("--n", type=int, default=10)
    args = parser.parse_args()

    records = []
    for name, build in FAMILIES.items():
        adjacency = build(args.n)
        predicted = algebraic_connectivity(adjacency)
        exact = EXACT[name](args.n)
        for seed in range(args.seeds):
            history, dt = simulate(laplacian(adjacency), seed=seed)
            records.append(
                {
                    "family": name,
                    "n": args.n,
                    "seed": seed,
                    "predicted": predicted,
                    "exact": exact,
                    "measured": decay_rate(history, dt),
                    "floor": baselines.mean_degree(adjacency),
                }
            )

    with open("results.json", "w") as handle:
        json.dump({"assumptions": ASSUMPTIONS, "records": records}, handle, indent=2)

    print(f"{'graph':>9} {'yours':>9} {'algebra':>9} {'measured':>9} {'floor':>7}")
    for name in FAMILIES:
        rows = [r for r in records if r["family"] == name]
        print(
            f"{name:>9} {rows[0]['predicted']:>9.4f} {rows[0]['exact']:>9.4f} "
            f"{np.nanmean([r['measured'] for r in rows]):>9.4f} {rows[0]['floor']:>7.2f}"
        )
    print("\nColumns 'yours' and 'algebra' should match once method.py is yours, and 'measured' should follow.")


if __name__ == "__main__":
    main()
