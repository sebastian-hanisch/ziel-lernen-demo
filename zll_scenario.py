"""Szenario: Zuordnung von n Personen auf n Aufgaben mit zwei Matrizen aus ganzen Zahlen (Kosten c1, Zeit c2); der Entscheider kann sich verschätzen. Alles simuliert.

Beide Matrizen unabhängig, ganze Zahlen 11 bis 109, erst c1, dann c2 aus einem Zufallsstrom (Seed); der Schätzfehler des Entscheiders stammt aus einem zweiten Strom (Seed * 7 + 1).
Die Erzeugung entspricht der Messreihe der Planung bis auf den Versatz 10 (Ecken und Haltepunkte sind gleich, nur die verrauschten Zahlen weichen ab)."""

import numpy as np

import zll_constants as C


def make_pair(n: int, seed: int) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    return (rng.integers(C.COST_LOW, C.COST_HIGH + 1, (n, n)).astype(np.int64), rng.integers(C.COST_LOW, C.COST_HIGH + 1, (n, n)).astype(np.int64))


def estimate_pair(c1: np.ndarray, c2: np.ndarray, a: int, seed: int) -> tuple[np.ndarray, np.ndarray]:
    """Die Kosten, mit denen der Entscheider rechnet: jede Zahl um eine ganze Zahl von -a bis +a verschoben (gleichverteilt, mindestens 1)."""
    if a == 0:
        return c1, c2
    rng = np.random.default_rng(seed * 7 + 1)
    return np.maximum(1, c1 + rng.integers(-a, a + 1, c1.shape)), np.maximum(1, c2 + rng.integers(-a, a + 1, c2.shape))
