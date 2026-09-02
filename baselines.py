"""A floor and a ceiling, so a number from `method.py` means something on day one."""

from __future__ import annotations

import numpy as np


def zero_rate(adjacency: np.ndarray) -> float:
    """"Nobody ever agrees." The floor."""
    return 0.0


def mean_degree(adjacency: np.ndarray) -> float:
    """A plausible-looking wrong answer: the average degree. Often close, never right."""
    return float(np.asarray(adjacency).sum(axis=1).mean())


def oracle(name: str, n: int) -> float:
    """The closed form for a named graph. The ceiling."""
    from synthetic import EXACT

    return EXACT[name](n)
