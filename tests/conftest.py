"""Gemeinsame Fixtures: zwei Handbeispiele (2 Personen, 2 Aufgaben), von Hand gerechnet, und die Zählungen über feste Instanzen (einmal je Testlauf)."""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import zll_algorithm as A  # noqa: E402
import zll_evaluation as ev  # noqa: E402

# Beispiel A: Plan 0 (Diagonale) hat Kosten 3 und Zeit 11, Plan 1 (Kreuz) Kosten 7 und Zeit 3; Haltepunkt 4 / (4 + 8) = 1/3.
HAND_A1 = np.array([[1, 4], [3, 2]], dtype=np.int64)
HAND_A2 = np.array([[5, 1], [2, 6]], dtype=np.int64)
# Beispiel B: Plan 0 hat Kosten 3 und Zeit 8, Plan 1 Kosten 7 und Zeit 3; Haltepunkt 4 / (4 + 5) = 4/9.
HAND_B1 = np.array([[2, 3], [4, 1]], dtype=np.int64)
HAND_B2 = np.array([[3, 2], [1, 5]], dtype=np.int64)


def hand_pair(c1, c2) -> A.Pair:
    return A.build_pair(c1, c2)


@pytest.fixture
def hand_a():
    return hand_pair(HAND_A1, HAND_A2)


@pytest.fixture
def hand_b():
    return hand_pair(HAND_B1, HAND_B2)


@pytest.fixture(scope="session")
def sweeps():
    """Die vier Zählungen über feste Instanzen (je einige Dutzend Sekunden); Rohdaten und Zusammenfassungen."""
    ex, no, ep = ev.sweep_exact(), ev.sweep_noise(), ev.sweep_eps()
    return {"exact": ev.summary_exact(ex), "noise": ev.summary_noise(no), "eps": ev.summary_eps(ep), "units": ev.sweep_units(), "raw_exact": ex, "raw_noise": no, "raw_eps": ep}
