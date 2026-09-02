"""The ruler's own tests. These pass on a fresh clone.

The ruler here does real work — it simulates a fleet and fits a rate — so it needs its own ground
truth, and it has one: a ring's lambda_2 is known in closed form.
"""

from __future__ import annotations

import numpy as np

from evaluate import decay_rate, simulate
from synthetic import EXACT, complete, ring


def true_laplacian(adjacency):
    return np.diag(adjacency.sum(axis=1)) - adjacency


def test_the_measured_rate_matches_algebra_on_a_ring():
    n = 8
    history, dt = simulate(true_laplacian(ring(n)))
    assert abs(decay_rate(history, dt) - EXACT["ring"](n)) / EXACT["ring"](n) < 0.05


def test_the_measured_rate_matches_algebra_on_a_complete_graph():
    n = 6
    history, dt = simulate(true_laplacian(complete(n)), dt=0.002)
    assert abs(decay_rate(history, dt) - EXACT["complete"](n)) / EXACT["complete"](n) < 0.10


def test_disagreement_actually_decays():
    history, _ = simulate(true_laplacian(ring(10)))
    assert history[-1] < history[0] * 1e-3
