"""Jede Zahl aus dem README wird hier nachgerechnet (DEMO-PLAYBOOK §4). Aufzählung und feste Instanzerzeugung sind deterministisch."""

from pathlib import Path

import pytest

import zll_constants as C
import zll_evaluation as ev

README = (Path(__file__).resolve().parent.parent / "README.md").read_text(encoding="utf-8")
(P_FIVE, P_ONE, P_TWENTY, P_EMPTY, P_SPLIT, P_EPS, P_UNIT, P_SMALL) = list(C.PRESETS)
KS = C.SWEEP_KS


def _claim(text):
    assert text in README, text


def _slash(values, fmt):
    return " / ".join(fmt(v) for v in values)


d1 = lambda x: ev.de(x, 1)
d0 = lambda x: ev.de(x, 0)
p1 = lambda x: ev.pct(x)


def _tsd(n):
    """Tausendertrennung mit schmalem Leerzeichen wie im README (hier: gewöhnliches Leerzeichen)."""
    return f"{n:,}".replace(",", " ")


def _t(name):
    return ev.trial(ev.Settings(**C.PRESETS[name]))


def _ex(name):
    return ev.explain(_t(name))


# --- Zählungen --------------------------------------------------------------------------------------------------------------------------------

def test_exact_widths_errors_and_predictions(sweeps):
    per = sweeps["exact"]["per"]
    _claim(f"**{_slash([per[K]['width'][1] for K in KS], d1)}**")
    _claim(_slash([per[K]["width"][2] for K in KS], d1))
    _claim(_slash([per[K]["within5"] for K in KS], str))
    _claim(f"{_slash([per[K]['err'][1] for K in KS], d1)}; Maximum {_slash([per[K]['err'][2] for K in KS], d1)}")
    _claim(_slash([_tsd(per[K]["hits"]) for K in KS], str))
    _claim(f"**{_slash([per[K]['hits'] / per[K]['n_pred'] * 100 for K in KS], d1)} %**")
    _claim(f"Maximum {_slash([per[K]['regret'][1] * 100 for K in KS], d1)} %")
    assert all(per[K]["regret"][0] == 0 for K in KS) and all(per[K]["contains"] == 180 for K in KS)
    _claim("**180 von 180**")


def test_noise_counts(sweeps):
    s = sweeps["noise"]
    per = s["per"]
    _claim(f"**{s['single_unexplained']} von {_tsd(s['single_n'])} ({ev.pct(s['single_unexplained'] / s['single_n'])})**")
    _claim(f"{_slash([per[K]['nonempty'] for K in KS[:-1]], str)} / **{per[KS[-1]]['nonempty']}**")
    _claim(_slash([per[K]["width"] for K in KS[:-1]], d1))
    _claim(f"**{_slash([per[K]['err_fit'][1] for K in KS], lambda x: ev.de(x, 1 if x % 1 else 0))}**")
    _claim(f"Maximum {_slash([per[K]['err_fit'][2] for K in KS], d0)}")
    _claim(_slash([_tsd(per[K]["hits_fit"]) for K in KS], str))
    _claim(_slash([per[K]["hits_fit"] / per[K]["n_pred"] * 100 for K in KS], d1) + " %")


def test_eps_and_lexicographic_counts(sweeps):
    s = sweeps["eps"]
    fr = list(s["eps"].values())
    _claim(f"**{_slash([v['explained'] for v in fr], str)}** ({_slash([v['explained'] / v['n'] * 100 for v in fr], d1)} %)")
    _claim(f"nur an einem Haltepunkt {_slash([v['point_only'] for v in fr], str)}; Breite (Median) {_slash([v['width'] for v in fr], d1)}")
    _claim(f"{_slash(s['lex'], d1)} Prozentpunkte")


def test_units_count(sweeps):
    u = sweeps["units"]
    _claim(f"**{u['changed']} von {u['n']}**; {u['same_corners']} von {u['n']}")


# --- Presets ----------------------------------------------------------------------------------------------------------------------------------

def test_main_preset():
    ex, ei = _ex(P_FIVE), ev.eps_info(_t(P_FIVE))
    _claim(f"Gewichte **{d1(ex['lo'])} bis {d1(ex['hi'])} %** (Breite {d1(ex['width'])}), wahres Gewicht 40 % darin, Mitte {d1(ex['mid'])} %")
    _claim(f"Vorhersage {ex['pred_mid']['hits']} von 20, robuste Anpassung ({ex['g_fit']} %) {ex['pred_fit']['hits']} von 20; ε-Constraint (40 %) in {ei['explained']} von 20 erklärbar")
    assert ex["contains"]


def test_one_decision_preset():
    ex = _ex(P_ONE)
    _claim(f"**{d1(ex['lo'])} bis 100 %** (Breite {d1(ex['width'])}), Mitte {d1(ex['mid'])} % ({d1(ex['err_mid'])} Prozentpunkte daneben), Vorhersage nur **{ex['pred_mid']['hits']} von 20**")
    _claim(f"die robuste Anpassung ({ex['g_fit']} %) trifft {ex['pred_fit']['hits']} von 20")
    assert ex["hi"] == 100.0


def test_twenty_preset():
    ex = _ex(P_TWENTY)
    _claim(f"**{d1(ex['lo'])} bis {d1(ex['hi'])} %** (Breite {d1(ex['width'])}), wahres Gewicht 30 %, Vorhersage {ex['pred_mid']['hits']} von 20")


def test_empty_preset():
    ex = _ex(P_EMPTY)
    assert ex["inter"] is None
    _claim(f"Menge **leer**, {ex['unexplained']} der 10 Entscheidungen schon einzeln nicht erklärbar; robuste Anpassung {ex['g_fit']} % gegen wahr {ex['w']} %, Vorhersage {ex['pred_fit']['hits']} von 20")


def test_split_preset():
    ex = _ex(P_SPLIT)
    assert ex["inter"] is None and ex["unexplained"] == 0
    _claim(f"robuste Anpassung {ex['g_fit']} % gleich dem wahren Gewicht, Vorhersage {ex['pred_fit']['hits']} von 20")


def test_eps_preset():
    ex, ei = _ex(P_EPS), ev.eps_info(_t(P_EPS))
    _claim(f"in **{ei['explained']} von 20** Entscheidungen durch ein Gewicht erklärbar; die Mitte der fünf Entscheidungen des Gewichts-Entscheiders ({d1(ex['mid'])} %) sagt {ex['pred_mid']['hits']} von 20 voraus")


def test_unit_preset():
    u = ev.unit_info(ev.Settings(**C.PRESETS[P_UNIT]))
    _claim(f"**{d1(float(u['interval_scaled'][0]) * 100)} bis 100 %** statt {d1(float(u['interval'][0]) * 100)} bis 100 %")
    assert u["interval_scaled"][1] == 1 and u["interval"][1] == 1


def test_small_preset():
    ex, ei = _ex(P_SMALL), ev.eps_info(_t(P_SMALL))
    _claim(f"**{d1(ex['lo'])} bis {d1(ex['hi'])} %** offen, Mitte {d1(ex['mid'])} %, Vorhersage {ex['pred_mid']['hits']} von 20; ε-Constraint in {ei['explained']} von 20 erklärbar")


# --- Korrektur der Planungshypothese ----------------------------------------------------------------------------------------------------------

def test_correction_numbers(sweeps):
    per = sweeps["exact"]["per"]
    _claim(f"({d1(per[1]['width'][1])} Prozentpunkte bei einer, {d1(per[20]['width'][1])} bei zwanzig)")
    _claim(f"(null von 180 nichtleer bei zwanzig;")
    assert sweeps["noise"]["per"][20]["nonempty"] == 0
    _claim(f"Breite bei K = 2 {d1(per[2]['width'][1])} statt 14,7, Vorhersage bei K = 20 {d1(per[20]['hits'] / per[20]['n_pred'] * 100)} statt 97,3 %, Schätzfehler: {sweeps['noise']['per'][1]['nonempty']} statt 150 nichtleere Mengen bei K = 1")


def test_readme_names_every_preset():
    for name in C.PRESETS:
        _claim(f"Preset „{name}“")


def test_readme_test_count_is_filled_in():
    assert "TESTZAHL" not in README
