"""The ruler. Complete, and it does not import `method`.

It simulates the fleet and fits the rate at which disagreement decays. That measured rate is what
the whole lab compares against algebra.
"""

from __future__ import annotations

import argparse

import numpy as np

from synthetic import EXACT, ring


def simulate(laplacian_matrix: np.ndarray, *, steps: int | None = None, dt: float | None = None, seed: int = 0):
    """Run xdot = -Lx and return (disagreement norm per step, dt).

    The step and the horizon are chosen from the matrix's own spectrum rather than fixed, because
    lambda_2 ranges over two orders of magnitude across these graphs. A step that is stable for a
    path graph diverges on a complete one, and a horizon that reaches the asymptote on a complete
    graph has barely started on a path. Both come straight out of the eigenvalues:

        dt <= 2 / lambda_max     for the forward Euler step to be stable at all
        T  ~  12 / lambda_2      long enough for the slow mode to dominate and decay

    This is the ruler measuring the system on the system's own timescale, which is the only way
    one fit can serve every graph.
    """
    eigenvalues = np.sort(np.linalg.eigvalsh(laplacian_matrix))
    lambda_max = float(eigenvalues[-1])
    lambda_2 = float(eigenvalues[1]) if len(eigenvalues) > 1 else 0.0

    # Resolve the decay with a fixed number of samples rather than a fixed step, so a complete
    # graph (fast) and a path graph (slow) are both measured over the same span of their own decay.
    horizon = 12.0 / lambda_2 if lambda_2 > 1e-12 else 40.0
    if dt is None:
        stable = 0.5 / lambda_max if lambda_max > 1e-12 else 0.01
        dt = min(horizon / 400.0, stable)
    if steps is None:
        steps = int(np.clip(horizon / dt, 200, 200_000))

    rng = np.random.default_rng(seed)
    x = rng.normal(size=laplacian_matrix.shape[0])
    x = x - x.mean()
    history = []
    for _ in range(steps):
        history.append(float(np.linalg.norm(x - x.mean())))
        x = x - dt * (laplacian_matrix @ x)
    return np.array(history), dt


def decay_rate(history: np.ndarray, dt: float, *, skip: float = 0.2) -> float:
    """Fit the exponential decay rate of the disagreement norm.

    The first stretch is discarded: fast modes dominate early, and the asymptotic rate is the one
    lambda_2 predicts. Fitting from t=0 gives a number that is too large and looks like a bug in
    the theory rather than a bug in the fit.
    """
    start = int(len(history) * skip)
    window = history[start:]
    # Relative to where the run started, not an absolute floor: a fleet whose disagreement began
    # at 0.3 has nothing left above 1e-12 long before the fit has enough points.
    usable = window > history[0] * 1e-9
    if usable.sum() < 10:
        return float("nan")
    t = np.arange(len(window))[usable] * dt
    slope = np.polyfit(t, np.log(window[usable]), 1)[0]
    return float(-slope)


def self_test() -> None:
    n = 8
    a = ring(n)
    true_l = np.diag(a.sum(axis=1)) - a
    predicted = EXACT["ring"](n)
    history, dt = simulate(true_l)
    print(f"ring({n}) lambda_2 by algebra : {predicted:.6f}")
    print(f"ring({n}) rate  by simulation : {decay_rate(history, dt):.6f}")
    print(f"relative difference           : {abs(decay_rate(history, dt) - predicted) / predicted:.2%}")
    print("\nThese two must agree. If they do not, the ruler is wrong and the lab has no ground truth.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    if parser.parse_args().self_test:
        self_test()
