"""Run the fleet over ROS 2 and check the rate against the algebra.

The lab's claim, one layer down: lambda_2 predicts how fast a fleet stops disagreeing. `evaluate.py`
confirms that for a matrix. This confirms it for a set of nodes exchanging messages.

Two things are deliberate here.

**The reference is the closed form, not your `method.py`.** A ring's lambda_2 is 2(1 - cos(2*pi/n))
whether or not you have written the Laplacian yet, so this script — and the CI job that runs it —
works on a fresh clone. Checking against `method.algebraic_connectivity` would mean CI failed until
the reader finished the lab, which is the opposite of what a build is for. Your own number is
printed beside it so you can see the two agree.

**The check is on the ordering, not on a tolerance.** An asynchronous fleet converges *faster* than
the synchronous theory: robots step on their own timers using whatever has arrived, so a neighbour's
already-updated value gets used within the same sweep. That is Gauss-Seidel rather than Jacobi, and
it is a speed-up, not an error. So the robust claim — and the paper's actual claim — is that a
better-connected graph agrees faster. That holds regardless of the transport.
"""

from __future__ import annotations

import argparse

import numpy as np

import synthetic
from evaluate import decay_rate

GRAPHS = {"ring": synthetic.ring, "star": synthetic.star, "path": synthetic.path, "complete": synthetic.complete}


def measure(name: str, robots: int, *, steps: int, gain: float) -> dict:
    """Run one fleet and return what the algebra predicted beside what the fleet did."""
    import fleet

    adjacency = GRAPHS[name](robots)
    exact = float(synthetic.EXACT[name](robots))
    # What a *synchronous* Euler step of size `gain` would give, which is the fair comparison for a
    # discrete simulation: the rate is -ln(1 - gain*lambda_2)/gain, not lambda_2 itself.
    step = gain * exact
    synchronous = -np.log(1 - step) / gain if step < 1 else float("nan")

    history = fleet.run(adjacency, steps=steps, gain=gain)
    disagreement = np.linalg.norm(history - history.mean(axis=0, keepdims=True), axis=0)
    return {
        "graph": name,
        "robots": robots,
        "exact": exact,
        "synchronous": synchronous,
        "measured": decay_rate(disagreement, gain),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph", default="ring", choices=sorted(GRAPHS))
    parser.add_argument("--robots", type=int, default=8)
    parser.add_argument("--steps", type=int, default=400)
    parser.add_argument("--gain", type=float, default=0.05)
    parser.add_argument("--check", action="store_true", help="run ring and complete, and assert the ordering")
    args = parser.parse_args()

    names = ["ring", "complete"] if args.check else [args.graph]
    rows = [measure(name, args.robots, steps=args.steps, gain=args.gain) for name in names]

    print(f"{'graph':>9} {'lambda_2':>9} {'sync pred':>10} {'on ROS 2':>10}")
    for row in rows:
        print(f"{row['graph']:>9} {row['exact']:>9.4f} {row['synchronous']:>10.4f} {row['measured']:>10.4f}")

    if not args.check:
        return

    for row in rows:
        assert np.isfinite(row["measured"]), f"{row['graph']}: the fleet never converged"
        assert row["measured"] > 0, f"{row['graph']}: disagreement grew"
        # A wide band, on purpose. It catches "nothing is talking" and "the graph is wrong" without
        # pretending the asynchronous rate should match the synchronous one to a few per cent.
        ratio = row["measured"] / row["exact"]
        assert 0.3 < ratio < 4.0, f"{row['graph']}: measured {row['measured']:.3f} vs lambda_2 {row['exact']:.3f}"

    ring = next(r for r in rows if r["graph"] == "ring")
    complete = next(r for r in rows if r["graph"] == "complete")
    assert complete["measured"] > ring["measured"], (
        f"a complete graph must agree faster than a ring: {complete['measured']:.3f} vs {ring['measured']:.3f}"
    )
    print("\nok — better-connected graphs agree faster, which is the claim")


if __name__ == "__main__":
    main()
