"""Your to-do list, as tests.

These fail against the placeholder in `method.py` and pass when it is the Laplacian. Run them with
`make check`. The order is the order to fix them in.
"""

from __future__ import annotations

import numpy as np
import pytest

from evaluate import decay_rate, simulate
from method import algebraic_connectivity, laplacian
from synthetic import EXACT, complete, path, random_connected, ring, star, two_islands


def test_the_laplacian_has_the_properties_a_laplacian_has():
    """Step 1. Rows sum to zero, it is symmetric, and it is positive semi-definite."""
    a = ring(7)
    l = laplacian(a)
    assert np.allclose(l.sum(axis=1), 0.0), "rows must sum to zero"
    assert np.allclose(l, l.T), "must be symmetric"
    assert np.linalg.eigvalsh(l).min() > -1e-9, "must be positive semi-definite"
    assert np.allclose(np.diag(l), a.sum(axis=1)), "the diagonal is the degree"


def test_the_smallest_eigenvalue_is_zero():
    """Step 2. The all-ones vector is always in the kernel — that is what "consensus" means."""
    l = laplacian(random_connected(10, seed=0))
    assert abs(np.linalg.eigvalsh(l).min()) < 1e-9


@pytest.mark.parametrize("name,build,n", [("complete", complete, 9), ("star", star, 9), ("ring", ring, 9), ("path", path, 9)])
def test_lambda_two_matches_the_closed_form(name, build, n):
    """Step 3. Four families whose lambda_2 you can compute by hand. No excuse for being wrong."""
    assert algebraic_connectivity(build(n)) == pytest.approx(EXACT[name](n), abs=1e-9)


def test_a_disconnected_fleet_never_agrees():
    """Step 4. Two islands with no link: lambda_2 is exactly zero, and consensus never happens."""
    assert algebraic_connectivity(two_islands(8)) == pytest.approx(0.0, abs=1e-9)


def test_the_predicted_rate_is_the_rate_the_fleet_actually_runs_at():
    """Step 5. The payoff. Simulate, fit the decay, and it must be the eigenvalue you computed."""
    a = ring(8)
    predicted = algebraic_connectivity(a)
    history, dt = simulate(laplacian(a))
    assert abs(decay_rate(history, dt) - predicted) / predicted < 0.05


@pytest.mark.xfail(reason="Step 6: the extension. Design a topology, do not just measure one.")
def test_a_better_topology_converges_faster():
    """Adding an edge where the Fiedler vector says to should beat adding one at random."""
    raise AssertionError("Maximise lambda_2 under a fixed edge count. See 'Past the paper'.")
