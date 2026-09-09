"""Predict the rate, then measure it, and write results.json."""

from __future__ import annotations

import argparse
import json
import math

import numpy as np

import baselines
from evaluate import decay_rate, simulate
from method import ASSUMPTIONS, algebraic_connectivity, laplacian
from synthetic import EXACT, complete, path, ring, star

def jsonable(record: dict) -> dict:
    """A record with every non-finite float replaced by ``None``.

    `json.dump` writes `NaN` and `Infinity` by default. Python reads those back; `JSON.parse`
    refuses them outright, so a single degenerate row makes the whole results file unreadable to
    anything that is not Python — including the course app that imports it. `null` is JSON, and it
    says the true thing: this one was not measured.

    The sanitising happens here, at the boundary, and not in the functions that compute the
    numbers. `float("nan")` is a perfectly good return value for a fit that had too few points, and
    the printed summary below still uses `np.nanmean` over the real values.
    """
    return {
        key: None if isinstance(value, float) and not math.isfinite(value) else value
        for key, value in record.items()
    }


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
        json.dump(
            {"assumptions": ASSUMPTIONS, "records": [jsonable(r) for r in records]},
            handle,
            indent=2,
            allow_nan=False,
        )

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
