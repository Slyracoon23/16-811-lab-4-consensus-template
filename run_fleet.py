"""Run the fleet over ROS 2 and check the rate against the algebra.

The lab's claim, one layer down: lambda_2 predicts how fast a fleet stops disagreeing. `evaluate.py`
confirms that for a matrix. This confirms it for eight processes exchanging messages.
"""

from __future__ import annotations

import argparse

import numpy as np

import synthetic
from evaluate import decay_rate
from method import algebraic_connectivity

GRAPHS = {"ring": synthetic.ring, "star": synthetic.star, "path": synthetic.path, "complete": synthetic.complete}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph", default="ring", choices=sorted(GRAPHS))
    parser.add_argument("--robots", type=int, default=8)
    parser.add_argument("--steps", type=int, default=400)
    parser.add_argument("--gain", type=float, default=0.05)
    parser.add_argument("--check", action="store_true", help="exit non-zero if the rate disagrees")
    args = parser.parse_args()

    import fleet

    adjacency = GRAPHS[args.graph](args.robots)
    predicted = algebraic_connectivity(adjacency)

    history = fleet.run(adjacency, steps=args.steps, gain=args.gain)
    disagreement = np.linalg.norm(history - history.mean(axis=0, keepdims=True), axis=0)
    measured = decay_rate(disagreement, args.gain)

    print(f"graph            : {args.graph} on {args.robots} robots")
    print(f"lambda_2         : {predicted:.4f}")
    print(f"measured on ROS 2: {measured:.4f}")
    if predicted > 1e-9 and np.isfinite(measured):
        print(f"relative gap     : {abs(measured - predicted) / predicted:.1%}")

    if args.check:
        assert np.isfinite(measured), "the fleet never converged; is every robot hearing anyone?"
        assert predicted > 1e-9, "this graph is disconnected; nothing to measure"
        gap = abs(measured - predicted) / predicted
        assert gap < 0.35, f"measured {measured:.4f} against lambda_2 {predicted:.4f} ({gap:.1%})"
        print("\nok — the fleet converges at the rate its graph allows")


if __name__ == "__main__":
    main()
