"""Eigenschaftstests (ORACLE-PLAYBOOK §5): Aussagen, die für jede Instanz und jedes verborgene Gewicht gelten müssen."""

from fractions import Fraction

import pytest

import zll_algorithm as A
import zll_constants as C
import zll_evaluation as ev
import zll_scenario as S

F = Fraction
SEEDS = (100000, 100020, 100040)
WS = (0, 1, 17, 40, 50, 83, 99, 100)


def _ex(seed, w, k=20, n=8, a=0, **kw):
    s = ev.Settings(n=n, seed=seed, w=w, k=k, a=a, **kw)
    t = ev.trial(s)
    return t, ev.explain(t)


@pytest.mark.parametrize("seed", SEEDS)
@pytest.mark.parametrize("w", WS)
def test_an_exact_decision_maker_is_always_explained_by_the_true_weight(seed, w):
    t, ex = _ex(seed, w)
    assert ex["unexplained"] == 0 and ex["inter"] is not None and ex["contains"]
    assert ex["lo"] <= w <= ex["hi"] and ex["lo"] <= ex["mid"] <= ex["hi"]


@pytest.mark.parametrize("seed", SEEDS)
def test_the_explaining_set_only_shrinks_with_more_decisions(seed):
    prev = (F(0), F(1))
    for k in range(1, C.K_MAX + 1):
        t = ev.trial(ev.Settings(seed=seed, w=40, k=k))
        inter = ev.explain(t)["inter"]
        assert inter is not None and prev[0] <= inter[0] and inter[1] <= prev[1]
        prev = inter


@pytest.mark.parametrize("seed", SEEDS)
@pytest.mark.parametrize("w", (10, 50, 90))
def test_the_chosen_plan_has_zero_regret_at_the_true_weight(seed, w):
    t, ex = _ex(seed, w)
    for d in t.decisions:
        assert A.regret(d["hull"], d["point"], w) == 0
    assert ex["fit_sums"][w] == 0


@pytest.mark.parametrize("seed", SEEDS)
@pytest.mark.parametrize("w", (10, 50, 90))
def test_the_robust_fit_of_an_exact_maker_lies_in_the_explaining_set(seed, w):
    t, ex = _ex(seed, w)
    assert ex["fit_sums"][ex["g_fit"]] == 0 and ex["inter"][0] <= F(ex["g_fit"], 100) <= ex["inter"][1]


@pytest.mark.parametrize("seed", SEEDS)
def test_corner_intervals_tile_the_weight_axis(seed):
    for j in range(5):
        hull, bps = ev._hull_of(8, seed + j)
        ivs = [A.interval_of_corner(list(bps), k) for k in range(len(hull))]
        assert ivs[0][0] == 0 and ivs[-1][1] == 1 and all(ivs[k][1] == ivs[k + 1][0] for k in range(len(ivs) - 1))
        assert all(lo < hi for lo, hi in ivs) and list(bps) == sorted(set(bps)) and all(0 < b < 1 for b in bps)


@pytest.mark.parametrize("seed", SEEDS)
def test_the_hull_has_growing_cost_and_falling_time(seed):
    for j in range(5):
        hull, _ = ev._hull_of(8, seed + j)
        assert [c[0] for c in hull] == sorted({c[0] for c in hull}) and [c[1] for c in hull] == sorted({c[1] for c in hull}, reverse=True)


@pytest.mark.parametrize("seed", SEEDS)
def test_prediction_counts_are_consistent(seed):
    t, ex = _ex(seed, 40, k=5)
    for key in ("pred_mid", "pred_fit"):
        p = ex[key]
        assert 0 <= p["hits"] <= p["n"] == C.N_TEST and len(p["regrets"]) == C.N_TEST and all(r >= 0 for r in p["regrets"])
        assert p["regret_max"] >= p["regret_median"] >= 0
        assert sum(r == 0 for r in p["regrets"]) >= p["hits"]          # ein richtiger Plan hat Regret 0


@pytest.mark.parametrize("seed", SEEDS)
def test_prediction_with_the_true_weight_is_perfect(seed):
    t, _ = _ex(seed, 40, k=1)
    p = ev._predict(t.tests, F(40, 100), 40)
    assert p["hits"] == p["n"] and p["regret_max"] == 0


@pytest.mark.parametrize("seed", SEEDS)
def test_noisy_maker_stays_within_the_estimate_error(seed):
    for j in range(5):
        c1, c2 = S.make_pair(8, seed + j)
        e1, e2 = S.estimate_pair(c1, c2, 5, seed + j)
        assert abs(e1 - c1).max() <= 5 and abs(e2 - c2).max() <= 5 and e1.min() >= 1 and e2.min() >= 1


@pytest.mark.parametrize("seed", SEEDS)
def test_lexicographic_interval_runs_from_zero_to_the_first_breakpoint(seed):
    t = ev.trial(ev.Settings(seed=seed))
    for d in t.decisions:
        assert d["lex"] == (F(0), d["bps"][0] if d["bps"] else F(1))


@pytest.mark.parametrize("seed", SEEDS)
def test_eps_choice_extremes(seed):
    for j in range(5):
        pair = A.build_pair(*S.make_pair(8, seed + j))
        assert int(pair.s2[A.eps_choice(pair.s1, pair.s2, 0)]) == int(pair.s2.min())          # Grenze 0: die beste Zeit
        assert int(pair.s1[A.eps_choice(pair.s1, pair.s2, 100)]) == int(pair.s1.min())         # Grenze 100: das Kosten-Optimum
        picks = [int(pair.s1[A.eps_choice(pair.s1, pair.s2, f)]) for f in range(0, 101, 10)]
        assert picks == sorted(picks, reverse=True)                                           # lockerere Grenze, nie höhere Kosten


@pytest.mark.parametrize("seed", SEEDS)
def test_time_in_other_units_keeps_the_corners_and_moves_the_interval_down(seed):
    for unit in range(1, len(C.UNITS)):
        u = ev.unit_info(ev.Settings(seed=seed, w=50, unit=unit))
        assert u["same_corners"]
        lo0, hi0 = u["interval"]
        lo1, hi1 = u["interval_scaled"]
        assert lo1 <= lo0 and hi1 <= hi0


def test_unit_factor_one_changes_nothing():
    u = ev.unit_info(ev.Settings(unit=0))
    assert u["factor"] == 1 and u["interval"] == u["interval_scaled"] and not u["changed"]
