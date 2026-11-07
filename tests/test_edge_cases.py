"""Randfälle: kleinstes und größtes n, ein Plan, alle Kosten gleich, gleiche Matrizen, Gewichtsenden, Schätzfehler am Rand, eine und zwanzig Entscheidungen."""

from fractions import Fraction

import numpy as np
import pytest

import zll_algorithm as A
import zll_constants as C
import zll_evaluation as ev
import zll_scenario as S
from conftest import hand_pair

F = Fraction


def test_one_person_has_one_plan_and_one_corner():
    c = np.array([[5]], dtype=np.int64)
    pair = hand_pair(c, c + 1)
    assert pair.hull == [(5, 6, 0)] and pair.bps == [] and A.corner_at(pair.hull, pair.bps, F(1, 3)) == 0
    assert A.explain_interval(pair.hull, pair.bps, (5, 6)) == (0, 1)


def test_all_costs_equal_means_every_plan_is_optimal_everywhere():
    c = np.full((4, 4), 7, dtype=np.int64)
    pair = hand_pair(c, c)
    assert len(pair.hull) == 1 and pair.hull[0][2] == 0 and pair.bps == []
    assert A.explain_interval(pair.hull, pair.bps, (28, 28)) == (0, 1)


def test_identical_criteria_give_a_single_corner():
    c1, _ = S.make_pair(5, 7)
    pair = hand_pair(c1, c1)
    assert len(pair.hull) == 1 and pair.bps == []


def test_a_corner_without_competitors_explains_every_weight_and_the_set_does_not_shrink():
    c = np.full((3, 3), 7, dtype=np.int64)
    pair = hand_pair(c, c)
    assert A.intersect([A.interval_of_corner(pair.bps, 0)] * 5) == (0, 1)


@pytest.mark.parametrize("w", [0, 100])
def test_weight_ends_are_explained(w):
    t = ev.trial(ev.Settings(w=w, k=20))
    ex = ev.explain(t)
    assert ex["inter"] is not None and ex["contains"] and ex["unexplained"] == 0
    assert (ex["lo"] == 0.0) if w == 0 else (ex["hi"] == 100.0)


def test_one_decision_and_twenty_decisions():
    one = ev.explain(ev.trial(ev.Settings(k=1)))
    twenty = ev.explain(ev.trial(ev.Settings(k=20)))
    assert len(one["intervals"]) == 1 and len(twenty["intervals"]) == 20 and twenty["width"] <= one["width"]


def test_smallest_instance_has_few_plans_and_still_works():
    t = ev.trial(ev.Settings(n=3, seed=100020, w=50, k=3))
    ex = ev.explain(t)
    assert ex["inter"] is not None and A.perms(3).shape[0] == 6 and ex["pred_mid"]["n"] == C.N_TEST


def test_largest_instance_enumerates_all_plans():
    assert A.perms(8).shape == (40320, 8)


def test_strongest_noise_gives_a_valid_fit_and_valid_counts():
    ex = ev.explain(ev.trial(ev.Settings(a=C.A_MAX, w=60, k=20)))
    assert 0 <= ex["g_fit"] <= 100 and 0 <= ex["unexplained"] <= 20 and 0 <= ex["pred_fit"]["hits"] <= 20
    assert ex["unexplained"] == 0 or ex["inter"] is None                   # ein einzeln nicht erklärbarer Plan macht den Schnitt leer


def test_estimate_pair_without_noise_returns_the_same_matrices():
    c1, c2 = S.make_pair(4, 9)
    e1, e2 = S.estimate_pair(c1, c2, 0, 9)
    assert e1 is c1 and e2 is c2


def test_noisy_decisions_do_not_depend_on_how_many_are_shown():
    a = ev.trial(ev.Settings(a=5, w=40, k=3)).decisions[:3]
    b = ev.trial(ev.Settings(a=5, w=40, k=10)).decisions[:3]
    assert [d["point"] for d in a] == [d["point"] for d in b]


def test_settings_defaults_match_the_constants():
    s = ev.Settings()
    assert (s.n, s.seed, s.w, s.k, s.a, s.frac, s.unit) == (C.DEFAULT_N, C.DEFAULT_SEED, C.DEFAULT_W, C.DEFAULT_K, C.DEFAULT_A, C.DEFAULT_FRAC, C.DEFAULT_UNIT)


def test_eps_info_counts_are_consistent():
    for frac in (0, 40, 100):
        info = ev.eps_info(ev.trial(ev.Settings(frac=frac)))
        assert info["n"] == 20 and info["explained"] == len(info["widths"]) and info["point_only"] <= info["explained"] and len(info["lex_widths"]) == 20


def test_formatting_helpers():
    assert ev.de(0.04, 1) == "0,0" and ev.de(-0.0) == "0,0" and ev.pct(0.1234) == "12,3 %" and ev.pp(5.94) == "5,9"
