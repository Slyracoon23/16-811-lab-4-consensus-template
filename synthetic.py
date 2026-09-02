"""Graphs whose spectrum is known in closed form.

This is what makes the lab checkable. You do not have to trust an eigenvalue solver on a random
graph before you have watched it agree with algebra on a ring.

    complete K_n   lambda_2 = n
    star   S_n     lambda_2 = 1                         (one centre, n-1 leaves)
    ring   C_n     lambda_2 = 2(1 - cos(2*pi/n))
    path   P_n     lambda_2 = 2(1 - cos(pi/n))
"""

from __future__ import annotations

import numpy as np


def complete(n: int) -> np.ndarray:
    return np.ones((n, n)) - np.eye(n)


def star(n: int) -> np.ndarray:
    a = np.zeros((n, n))
    a[0, 1:] = a[1:, 0] = 1.0
    return a


def ring(n: int) -> np.ndarray:
    a = np.zeros((n, n))
    for i in range(n):
        a[i, (i + 1) % n] = a[(i + 1) % n, i] = 1.0
    return a


def path(n: int) -> np.ndarray:
    a = np.zeros((n, n))
    for i in range(n - 1):
        a[i, i + 1] = a[i + 1, i] = 1.0
    return a


def two_islands(n: int = 8) -> np.ndarray:
    """Two cliques with no edge between them. Disconnected, so lambda_2 must be 0."""
    a = np.zeros((n, n))
    half = n // 2
    a[:half, :half] = complete(half)
    a[half:, half:] = complete(n - half)
    return a


def random_connected(n: int = 12, *, p: float = 0.35, seed: int = 0) -> np.ndarray:
    """A random graph, resampled until connected. The case with no closed form."""
    rng = np.random.default_rng(seed)
    for _ in range(500):
        upper = (rng.random((n, n)) < p).astype(float)
        a = np.triu(upper, 1)
        a = a + a.T
        degrees = a.sum(axis=1)
        if degrees.min() == 0:
            continue
        laplacian = np.diag(degrees) - a
        if np.sort(np.linalg.eigvalsh(laplacian))[1] > 1e-9:
            return a
    raise RuntimeError("no connected graph found; raise p")


EXACT = {
    "complete": lambda n: float(n),
    "star": lambda n: 1.0,
    "ring": lambda n: 2 * (1 - np.cos(2 * np.pi / n)),
    "path": lambda n: 2 * (1 - np.cos(np.pi / n)),
}
