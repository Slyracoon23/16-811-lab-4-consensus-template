"""The technique. This is the only file in the repository you have to write.

What ships here runs and is wrong: it returns a zero Laplacian, so every graph looks disconnected
and nothing ever agrees. The harness is proved before you touch it.

What you are implementing (Gallier & Quaintance ch. 18; Olfati-Saber & Murray 2004):

    L = D - A                        degree matrix minus adjacency. That is the Laplacian.
    lambda_2 = second-smallest eigenvalue of L

The claim the lab tests is that lambda_2 is not a summary of the graph but the *rate* at which a
fleet running xdot = -Lx stops disagreeing. The Laplacian is not background here. It is the
controller.

L is symmetric positive semi-definite, so use `eigvalsh`, not `eigvals`: the symmetric solver is
faster and returns real eigenvalues in order instead of complex ones with 1e-17 imaginary parts.
"""

from __future__ import annotations

import numpy as np

ASSUMPTIONS: list[str] = [
    "The graph is undirected and unweighted: A is symmetric with a zero diagonal.",
    "Every robot can talk to its neighbours instantly. Delay is step 4's problem.",
]


def laplacian(adjacency: np.ndarray) -> np.ndarray:
    """Return the graph Laplacian L = D - A."""
    a = np.asarray(adjacency, dtype=float)

    # PLACEHOLDER — runs, and is wrong: every graph looks disconnected.
    return np.zeros_like(a)


def algebraic_connectivity(adjacency: np.ndarray) -> float:
    """Return lambda_2 of the Laplacian: the Fiedler value, and the consensus rate."""
    eigenvalues = np.linalg.eigvalsh(laplacian(adjacency))
    return float(np.sort(eigenvalues)[1]) if len(eigenvalues) > 1 else 0.0


def fiedler_vector(adjacency: np.ndarray) -> np.ndarray:
    """The eigenvector for lambda_2. Chapter 19 draws the fleet with it; the straggler is visible."""
    values, vectors = np.linalg.eigh(laplacian(adjacency))
    return vectors[:, np.argsort(values)[1]]
