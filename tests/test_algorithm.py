"""Kern von Hand: zwei Handbeispiele, Haltepunkte, Intervalle, Schnitt, Regret, Anpassung und die Wahl des ε-Constraint-Entscheiders."""

from fractions import Fraction

import numpy as np
import pytest

import zll_algorithm as A
from conftest import HAND_A1, HAND_A2, HAND_B1, HAND_B2, hand_pair

F = Fraction


def test_hand_example_a_has_two_corners_and_one_breakpoint(hand_a):
    assert hand_a.hull == [(3, 11, 0), (7, 3, 1)] and hand_a.bps == [F(1, 3)]
    assert list(hand_a.s1) == [3, 7] and list(hand_a.s2) == [11, 3]


def test_hand_example_b(hand_b):
    assert hand_b.hull == [(3, 8, 0), (7, 3, 1)] and hand_b.bps == [F(4, 9)]


def test_corner_at_switches_at_the_breakpoint_and_the_tie_goes_to_the_smaller_index(hand_a):
    h, b = hand_a.hull, hand_a.bps
    assert A.corner_at(h, b, F(0)) == 0 and A.corner_at(h, b, F(33, 100)) == 0
    assert A.corner_at(h, b, F(1, 3)) == 0                      # Gleichstand: Plan 0 hat den kleineren Index
    assert A.corner_at(h, b, F(34, 100)) == 1 and A.corner_at(h, b, F(1)) == 1


def test_tie_goes_to_the_smaller_index_even_when_the_second_corner_has_it():
    hull = [(3, 11, 1), (7, 3, 0)]                               # dieselben Punkte, die Indizes vertauscht
    bps = [F(1, 3)]
    assert A.corner_at(hull, bps, F(1, 3)) == 1                  # Ecke 1 hat den Plan mit Index 0
    assert A.corner_at(hull, bps, F(1, 4)) == 0 and A.corner_at(hull, bps, F(1, 2)) == 1


def test_interval_of_corner(hand_a):
    assert A.interval_of_corner(hand_a.bps, 0) == (F(0), F(1, 3)) and A.interval_of_corner(hand_a.bps, 1) == (F(1, 3), F(1))
    assert A.interval_of_corner([], 0) == (F(0), F(1))


def test_explain_interval_corner_edge_point_and_none(hand_a):
    h, b = hand_a.hull, hand_a.bps
    assert A.explain_interval(h, b, (3, 11)) == (F(0), F(1, 3))
    assert A.explain_interval(h, b, (7, 3)) == (F(1, 3), F(1))
    assert A.explain_interval(h, b, (5, 7)) == (F(1, 3), F(1, 3))      # Mitte der Kante: nur am Haltepunkt optimal
    assert A.explain_interval(h, b, (9, 9)) is None                    # über der Hülle: nie optimal
    assert A.explain_interval(h, b, (5, 8)) is None


def test_intersect_of_the_two_hand_examples(hand_a, hand_b):
    ia = A.interval_of_corner(hand_a.bps, 1)                           # A: Plan 1 gewählt, w >= 1/3
    ib = A.interval_of_corner(hand_b.bps, 0)                           # B: Plan 0 gewählt, w <= 4/9
    assert A.intersect([ia, ib]) == (F(1, 3), F(4, 9))
    lo, hi = A.intersect([ia, ib])
    assert (lo + hi) / 2 == F(7, 18)                                   # Mitte 38,9 %


def test_intersect_edge_cases():
    assert A.intersect([(F(0), F(1, 3)), (F(1, 3), F(1))]) == (F(1, 3), F(1, 3))      # berühren sich: ein Punkt
    assert A.intersect([(F(0), F(1, 4)), (F(1, 3), F(1))]) is None                    # leer
    assert A.intersect([(F(0), F(1)), None]) is None                                  # ein Intervall fehlt
    assert A.intersect([(F(1, 5), F(3, 5))]) == (F(1, 5), F(3, 5))


def test_value_regret_and_the_fit_by_hand(hand_a):
    h = hand_a.hull
    assert A.value(h, 50) == 500 and A.value(h, 0) == 300 and A.value(h, 100) == 300
    assert A.regret(h, (3, 11), 50) == F(2, 5) and A.regret(h, (7, 3), 50) == 0
    assert A.regret(h, (3, 11), 34) == F(572 - 564, 564)


def test_robust_fit_of_one_decision_is_the_smallest_weight_with_zero_regret(hand_a):
    g, sums = A.robust_fit([(3, 11)], [hand_a.hull])
    assert g == 0 and sums[33] == 0 and sums[34] > 0                   # Plan 0 ist bis 33 % optimal; Gleichstand: das kleinere Gewicht
    g2, _ = A.robust_fit([(7, 3)], [hand_a.hull])
    assert g2 == 34                                                    # Plan 1 ist ab 34 % (33 % wäre noch Plan 0 plus Rest) optimal


def test_robust_fit_of_two_conflicting_decisions_minimises_the_sum(hand_a, hand_b):
    pts = [(3, 11), (7, 3)]                                            # zwei Entscheidungen auf derselben Instanz: Plan 0 (w <= 1/3) und Plan 1 (w >= 1/3), sie überschneiden sich nur am Haltepunkt
    g, sums = A.robust_fit(pts, [hand_a.hull, hand_a.hull])
    assert min(sums) == sums[g] and sums[g] > 0
    assert g in (33, 34)                                               # der Kompromiss liegt am Haltepunkt


def test_eps_choice_by_hand(hand_a):
    s1, s2 = hand_a.s1, hand_a.s2
    assert A.eps_choice(s1, s2, 0) == 1                                # beste Zeit
    assert A.eps_choice(s1, s2, 50) == 1                               # Grenze 3 + 4 = 7: nur Plan 1 erreicht sie
    assert A.eps_choice(s1, s2, 100) == 0                              # Grenze 11: beide, der billigere gewinnt


@pytest.mark.parametrize("n", [3, 4, 5])
def test_perms_counts_and_order(n):
    P = A.perms(n)
    import itertools
    assert P.shape[0] == len(list(itertools.permutations(range(n)))) and [tuple(r) for r in P] == list(itertools.permutations(range(n)))


def test_perms_refuses_n_above_eight():
    with pytest.raises(ValueError):
        A.perms(9)


def test_scaled_time_keeps_the_corners_and_moves_the_breakpoint(hand_a):
    scaled = hand_pair(HAND_A1, HAND_A2 * 10)
    assert [c[2] for c in scaled.hull] == [c[2] for c in hand_a.hull]
    assert scaled.bps == [F(4, 4 + 80)] == [F(1, 21)]


def test_planning_example_b_with_all_four_combinations():
    """Instanz B der Planung: Kosten [[1, 5], [5, 1]], Zeit [[5, 1], [1, 5]]: Diagonale (2, 10), Kreuz (10, 2), Haltepunkt 1/2."""
    b = hand_pair(np.array([[1, 5], [5, 1]]), np.array([[5, 1], [1, 5]]))
    a = hand_pair(HAND_A1, HAND_A2)
    assert b.hull == [(2, 10, 0), (10, 2, 1)] and b.bps == [F(1, 2)]
    diag_a, cross_a = A.interval_of_corner(a.bps, 0), A.interval_of_corner(a.bps, 1)
    diag_b, cross_b = A.interval_of_corner(b.bps, 0), A.interval_of_corner(b.bps, 1)
    assert A.intersect([cross_a, diag_b]) == (F(1, 3), F(1, 2))                       # Breite 1/6, Mitte 5/12
    assert A.intersect([diag_a, cross_b]) is None                                    # kein Gewicht erklärt beide
    assert A.intersect([cross_a, cross_b]) == (F(1, 2), F(1)) and A.intersect([diag_a, diag_b]) == (F(0), F(1, 3))
    lo, hi = A.intersect([cross_a, diag_b])
    assert (lo + hi) / 2 == F(5, 12)


def test_planning_example_robust_fit_of_the_empty_case_lies_at_the_edge_of_b():
    a = hand_pair(HAND_A1, HAND_A2)
    b = hand_pair(np.array([[1, 5], [5, 1]]), np.array([[5, 1], [1, 5]]))
    g, sums = A.robust_fit([(3, 11), (10, 2)], [a.hull, b.hull])                      # A: Diagonale, B: Kreuz
    assert g == 50 and float(sums[50]) == pytest.approx(0.4) and float(sums[49]) == pytest.approx(0.4, abs=1e-3)
