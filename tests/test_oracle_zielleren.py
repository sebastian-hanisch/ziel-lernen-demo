"""Orakel (ORACLE-PLAYBOOK §5): reines Python (`itertools.permutations`, Schleifen, `Fraction`), keine numpy-Zeile im Referenzweg.

Die erklärende Menge eines Punktes (s1, s2) wird aus der Definition gerechnet: alle Gewichte, bei denen der Plan unter allen Plänen minimal ist. Diese Menge ist ein abgeschlossenes Intervall,
seine Enden liegen unter den Schnittpunkten je zweier Pläne und den Enden 0 und 1; an den Enden gilt der Grenzwert (bei 0 zählt zuerst die Kosten-Summe, bei 1 zuerst die Zeit-Summe)."""

import itertools
import random
from fractions import Fraction

import numpy as np
import pytest

import zll_algorithm as A
import zll_scenario as S
from conftest import hand_pair

F = Fraction
CASES = [(n, seed) for n in (3, 4) for seed in (1, 2, 3, 4, 5, 6)]


def _matrices(n, seed):
    rng = random.Random(seed * 100 + n)
    return [[rng.randint(11, 109) for _ in range(n)] for _ in range(n)], [[rng.randint(11, 109) for _ in range(n)] for _ in range(n)]


def _points(c1, c2):
    n = len(c1)
    return [(sum(c1[i][p[i]] for i in range(n)), sum(c2[i][p[i]] for i in range(n))) for p in itertools.permutations(range(n))]


def _candidates(pts):
    uniq = sorted(set(pts))
    cross = {F(0), F(1)}
    for (a1, a2), (b1, b2) in itertools.combinations(uniq, 2):
        den = (b1 - a1) + (a2 - b2)
        if den != 0:
            w = F(b1 - a1, den)
            if 0 < w < 1:
                cross.add(w)
    return sorted(cross)


def _bests(pts, cand):
    """Je Kandidat der kleinste Wert (an den Enden der Grenzwert als Paar), einmal gerechnet."""
    out = {}
    for g in cand:
        if g == 0:
            out[g] = min(pts)
        elif g == 1:
            out[g] = min((q[1], q[0]) for q in pts)
        else:
            out[g] = min((1 - g) * q[0] + g * q[1] for q in pts)
    return out


def _is_min(bests, pt, g):
    """Ist der Punkt beim Gewicht g (mit Grenzwert an den Enden) ein Minimierer?"""
    if g == 0:
        return (pt[0], pt[1]) == bests[g]
    if g == 1:
        return (pt[1], pt[0]) == bests[g]
    return (1 - g) * pt[0] + g * pt[1] == bests[g]


def _ref_interval(bests, cand, pt):
    ok = [g for g in cand if _is_min(bests, pt, g)]
    return (ok[0], ok[-1]) if ok else None


@pytest.mark.parametrize("n,seed", CASES)
def test_explained_intervals_match_the_definition_for_every_point(n, seed):
    c1, c2 = _matrices(n, seed)
    pts = _points(c1, c2)
    cand = _candidates(pts)
    bests = _bests(pts, cand)
    pair = A.build_pair(np.array(c1), np.array(c2))
    for pt in sorted(set(pts)):
        assert A.explain_interval(pair.hull, pair.bps, pt) == _ref_interval(bests, cand, pt), pt


@pytest.mark.parametrize("seed", [1, 2, 3])
def test_explained_intervals_n5_sampled_points(seed):
    c1, c2 = _matrices(5, seed)
    pts = _points(c1, c2)
    cand = _candidates(pts)
    bests = _bests(pts, cand)
    pair = A.build_pair(np.array(c1), np.array(c2))
    rng = random.Random(seed)
    sample = [(c[0], c[1]) for c in pair.hull] + rng.sample(sorted(set(pts)), 10)
    for pt in sample:
        assert A.explain_interval(pair.hull, pair.bps, pt) == _ref_interval(bests, cand, pt), pt


@pytest.mark.parametrize("n,seed", CASES)
def test_chosen_plan_is_a_minimiser_and_the_smallest_index_off_the_breakpoints(n, seed):
    c1, c2 = _matrices(n, seed)
    pts = _points(c1, c2)
    pair = A.build_pair(np.array(c1), np.array(c2))
    for g in range(0, 101):
        w = F(g, 100)
        vals = [(1 - w) * p[0] + w * p[1] for p in pts]
        best = min(vals)
        minimisers = [i for i, v in enumerate(vals) if v == best]
        k = A.corner_at(pair.hull, pair.bps, w)
        idx = pair.hull[k][2]
        assert idx in minimisers
        if w not in pair.bps:
            assert idx == minimisers[0]                      # eindeutiger Punkt, kleinster Index unter gleichen Punkten


def _ref_eps(c1, c2, frac):
    pts = _points(c1, c2)
    s2min = min(p[1] for p in pts)
    first_min_s1 = min(range(len(pts)), key=lambda i: (pts[i][0], i))
    limit = s2min + F(frac, 100) * (pts[first_min_s1][1] - s2min)
    ok = [i for i, p in enumerate(pts) if p[1] <= limit]
    return min(ok, key=lambda i: (pts[i][0], i))


@pytest.mark.parametrize("n,seed", CASES)
def test_eps_choice_matches_the_definition(n, seed):
    c1, c2 = _matrices(n, seed)
    P = A.perms(n)
    s1, s2 = A.plan_sums(np.array(c1), P), A.plan_sums(np.array(c2), P)
    for frac in range(0, 101, 10):
        assert A.eps_choice(s1, s2, frac) == _ref_eps(c1, c2, frac), frac


@pytest.mark.parametrize("n,seed", CASES)
def test_robust_fit_matches_a_plain_loop(n, seed):
    c1, c2 = _matrices(n, seed)
    c1b, c2b = _matrices(n, seed + 50)
    inst = [(c1, c2), (c1b, c2b)]
    chosen = []
    for k, (a, b) in enumerate(inst):
        pts = _points(a, b)
        chosen.append(pts[(seed * 7 + k * 3) % len(pts)])             # ein beliebiger beobachteter Plan je Instanz
    sums = []
    for g in range(101):
        total = F(0)
        for (a, b), pt in zip(inst, chosen):
            pts = _points(a, b)
            best = min((100 - g) * q[0] + g * q[1] for q in pts)
            total += F((100 - g) * pt[0] + g * pt[1] - best, best)
        sums.append(total)
    best_g = min(range(101), key=lambda g: (sums[g], g))
    hulls = [A.build_pair(np.array(a), np.array(b)).hull for a, b in inst]
    g, got = A.robust_fit(chosen, hulls)
    assert g == best_g and list(got) == sums


def test_make_pair_is_deterministic_and_inside_the_cost_range():
    c1, c2 = S.make_pair(5, 123)
    d1, d2 = S.make_pair(5, 123)
    assert (c1 == d1).all() and (c2 == d2).all() and c1.min() >= 11 and c1.max() <= 109 and c2.min() >= 11 and c2.max() <= 109 and not (c1 == c2).all()
    assert not (S.make_pair(5, 124)[0] == c1).all()


def test_hand_pair_roundtrips():
    from conftest import HAND_A1, HAND_A2
    assert hand_pair(HAND_A1, HAND_A2).bps == [F(1, 3)]
