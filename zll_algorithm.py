"""Kern: Zuordnung mit zwei Kriterien (alle n! Pläne), die Gewichte, bei denen ein Plan optimal ist (Intervalle aus den Ecken der unteren konvexen Hülle), die Schnittmenge über Entscheidungen,
die robuste Anpassung und die Wahl eines ε-Constraint-Entscheiders. Alles in ganzen Zahlen und exakten Brüchen.

Ein Plan ist eine Permutation p (Person i macht Aufgabe p[i]), in der Reihenfolge von `itertools.permutations`; bei Gleichstand gilt der kleinste Index (Stück 5 der Linie).
Quelle der Ecken und Haltepunkte: Stück 11 der Linie (`planstabilitaet-demo`), neu geschrieben.
Das Ziel (1 - w) * Kosten + w * Zeit mit w als Anteil in 0 bis 1; die Pläne, die ein Gewicht findet, sind die Ecken der unteren konvexen Hülle der Punkte (Summe Kosten, Summe Zeit);
ein Plan ist genau bei einem Intervall von Gewichten optimal (Ecke), bei einem einzelnen Gewicht (Punkt auf einer Kante) oder bei keinem (jeder andere Plan)."""

import itertools
from bisect import bisect_right
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache

import numpy as np

import zll_constants as C

MAX_ENUM_N = 8


@lru_cache(maxsize=None)
def perms(n: int) -> np.ndarray:
    if n > MAX_ENUM_N:
        raise ValueError(f"n = {n} ist zu groß für die Aufzählung (höchstens {MAX_ENUM_N})")
    return np.array(list(itertools.permutations(range(n))), dtype=np.int8)


def plan_sums(c: np.ndarray, P: np.ndarray) -> np.ndarray:
    n = c.shape[0]
    return c[np.arange(n)[None, :], P.astype(np.int64)].sum(axis=1)


def corners(s1: np.ndarray, s2: np.ndarray) -> list[tuple[int, int, int]]:
    """Ecken der unteren konvexen Hülle (s1, s2, Plan-Index), von kleinem s1 nach großem s1; je Punkt der kleinste Index."""
    key = s1.astype(np.int64) * 10 ** 6 + s2
    order = np.lexsort((np.arange(len(key)), key))
    ks = key[order]
    first = np.concatenate(([True], ks[1:] != ks[:-1]))
    pts = sorted((int(s1[i]), int(s2[i]), int(i)) for i in order[first])
    chain, best2 = [], None
    for p in pts:
        if best2 is None or p[1] < best2:
            chain.append(p)
            best2 = p[1]
    hull: list[tuple[int, int, int]] = []
    for p in chain:
        while len(hull) >= 2:
            a, b = hull[-2], hull[-1]
            if (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]) <= 0:
                hull.pop()
            else:
                break
        hull.append(p)
    return hull


def breakpoints(hull: list) -> list[Fraction]:
    out = []
    for k in range(len(hull) - 1):
        d1, d2 = hull[k + 1][0] - hull[k][0], hull[k][1] - hull[k + 1][1]
        out.append(Fraction(d1, d1 + d2))
    return out


@dataclass
class Pair:
    s1: np.ndarray
    s2: np.ndarray
    hull: list
    bps: list


def build_pair(c1: np.ndarray, c2: np.ndarray) -> Pair:
    P = perms(c1.shape[0])
    s1, s2 = plan_sums(c1, P), plan_sums(c2, P)
    hull = corners(s1, s2)
    return Pair(s1, s2, hull, breakpoints(hull))


def corner_at(hull: list, bps: list, w: Fraction) -> int:
    """Index der Ecke, die beim Gewicht w optimal ist; am Haltepunkt selbst die mit dem kleineren Plan-Index (Gleichstandsregel)."""
    k = bisect_right(bps, w)
    if k > 0 and bps[k - 1] == w and hull[k - 1][2] < hull[k][2]:
        return k - 1
    return k


def interval_of_corner(bps: list, k: int) -> tuple[Fraction, Fraction]:
    """Die Gewichte, bei denen die Ecke k optimal ist (abgeschlossenes Intervall von Haltepunkt zu Haltepunkt)."""
    return (Fraction(0) if k == 0 else bps[k - 1]), (Fraction(1) if k == len(bps) else bps[k])


def explain_interval(hull: list, bps: list, point: tuple[int, int]) -> tuple[Fraction, Fraction] | None:
    """Die Gewichte, die einen Plan mit den Summen `point` als optimal erklären: ein Intervall (Ecke), ein Punkt (auf einer Kante der Hülle) oder None (kein Gewicht)."""
    for k, c in enumerate(hull):
        if (c[0], c[1]) == point:
            return interval_of_corner(bps, k)
    for k in range(len(hull) - 1):
        a, b = hull[k], hull[k + 1]
        if (b[0] - a[0]) * (point[1] - a[1]) - (b[1] - a[1]) * (point[0] - a[0]) == 0 and a[0] < point[0] < b[0]:
            return bps[k], bps[k]
    return None


def intersect(intervals: list) -> tuple[Fraction, Fraction] | None:
    """Schnittmenge von Intervallen; None bei leerer Menge (oder wenn ein Intervall selbst fehlt)."""
    if any(i is None for i in intervals):
        return None
    lo, hi = max(i[0] for i in intervals), min(i[1] for i in intervals)
    return (lo, hi) if lo <= hi else None


def value(hull: list, g_pct: int) -> int:
    """Kleinster Wert des Ziels (mal 100) beim Gewicht g in Prozent: das Optimum liegt immer an einer Ecke."""
    return min((100 - g_pct) * c[0] + g_pct * c[1] for c in hull)


def regret(hull: list, point: tuple[int, int], g_pct: int) -> Fraction:
    """Relativer Regret eines Plans beim Gewicht g in Prozent: (Wert - Optimum) / Optimum."""
    v = value(hull, g_pct)
    return Fraction((100 - g_pct) * point[0] + g_pct * point[1] - v, v)


def regret_rows(points: list, hulls: list) -> list[list[Fraction]]:
    """Je Entscheidung der relative Regret des beobachteten Plans bei jedem Gewicht des Rasters (ganze Prozent)."""
    return [[regret(h, pt, g) for g in C.GRID] for pt, h in zip(points, hulls)]


def fit_rows(rows: list[list[Fraction]], k: int) -> tuple[int, list[Fraction]]:
    """Das Gewicht (ganze Prozent) mit der kleinsten Summe der relativen Regrets der ersten k Entscheidungen; Gleichstand: das kleinere Gewicht. Rückgabe (Gewicht, Summe je Rasterpunkt)."""
    sums = [sum((r[g] for r in rows[:k]), Fraction(0)) for g in range(len(C.GRID))]
    best = min(range(len(sums)), key=lambda i: (sums[i], i))
    return C.GRID[best], sums


def robust_fit(points: list, hulls: list) -> tuple[int, list]:
    """Die robuste Anpassung aus den beobachteten Plänen (Summe Kosten, Summe Zeit) und den wahren Hüllen je Entscheidung."""
    return fit_rows(regret_rows(points, hulls), len(points))


def eps_choice(s1: np.ndarray, s2: np.ndarray, frac_pct: int) -> int:
    """Wahl eines ε-Constraint-Entscheiders: kleinste Kosten unter der Zeitgrenze, die frac Prozent des Weges von der besten Zeit zur Zeit des Kosten-Optimums beträgt (kleinster Index bei Gleichstand)."""
    s2_min = int(s2.min())
    nadir = int(s2[int(np.argmin(s1))])
    ok = np.flatnonzero(s2.astype(np.int64) * 100 <= s2_min * 100 + frac_pct * (nadir - s2_min))
    return int(ok[int(np.argmin(s1[ok]))])
