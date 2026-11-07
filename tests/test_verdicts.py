"""Verdikte: Art und Wortlaut in den Fällen, die sie unterscheiden (DEMO-PLAYBOOK §6): jede Zahl im Text kommt aus der Rechnung."""

import zll_constants as C
import zll_evaluation as ev

(P_FIVE, P_ONE, P_TWENTY, P_EMPTY, P_SPLIT, P_EPS, P_UNIT, P_SMALL) = list(C.PRESETS)


def _t(name):
    return ev.trial(ev.Settings(**C.PRESETS[name]))


def _ex(name):
    return ev.explain(_t(name))


def test_explain_verdict_with_a_nonempty_set():
    assert ev.verdict_explain(_ex(P_FIVE)) == ("info", "Nach 5 Entscheidungen erklären die Gewichte von 35,8 bis 41,7 % alle Entscheidungen (Breite **5,9 Prozentpunkte**); "
                                                       "das wahre Gewicht 40 % liegt darin, die Mitte 38,8 % liegt 1,2 Prozentpunkte daneben.")
    kind, text = ev.verdict_explain(_ex(P_ONE))
    assert kind == "info" and text.startswith("Nach 1 Entscheidung erklären die Gewichte von 57,5 bis 100,0 %") and "Breite **42,5 Prozentpunkte**" in text
    assert "Nach 20 Entscheidungen erklären die Gewichte von 29,4 bis 30,7 %" in ev.verdict_explain(_ex(P_TWENTY))[1]
    assert "von 42,1 bis 62,6 %" in ev.verdict_explain(_ex(P_SMALL))[1]


def test_explain_verdict_with_an_empty_set_names_single_failures():
    kind, text = ev.verdict_explain(_ex(P_EMPTY))
    assert kind == "warning" and text == ("**Kein Gewicht erklärt alle 10 Entscheidungen** (2 davon schon einzeln nicht). Die robuste Anpassung (kleinste Summe der Regrets) wählt 15 % gegen das wahre Gewicht 20 % "
                                          "(Fehler 5 Prozentpunkte).")
    kind, text = ev.verdict_explain(_ex(P_SPLIT))
    assert kind == "warning" and "davon schon einzeln nicht" not in text and "wählt 70 % gegen das wahre Gewicht 70 % (Fehler 0 Prozentpunkte)" in text


def test_explain_verdict_says_when_the_true_weight_is_not_inside():
    ex = {**_ex(P_FIVE), "contains": False}
    assert "liegt **nicht** darin" in ev.verdict_explain(ex)[1]


def test_predict_verdict_cases():
    assert ev.verdict_predict(_ex(P_FIVE))[1] == ("Auf 20 neuen Instanzen sagt die Mitte (38,8 %) 19 von 20 Plänen richtig voraus (Regret der falschen Pläne im Median 0,0 %, höchstens 0,1 %), "
                                                  "die robuste Anpassung (36 %) 17 von 20 Plänen.")
    assert "sagt die Mitte (78,8 %) 7 von 20 Plänen richtig voraus" in ev.verdict_predict(_ex(P_ONE))[1] and "die robuste Anpassung (58 %) 19 von 20 Plänen" in ev.verdict_predict(_ex(P_ONE))[1]
    assert ev.verdict_predict(_ex(P_EMPTY))[1] == ("Auf 20 neuen Instanzen sagt die robuste Anpassung (15 %) 19 von 20 Plänen richtig voraus (Regret der falschen Pläne im Median 0,0 %, höchstens 1,2 %); "
                                                   "die Mitte gibt es nicht, die Menge ist leer.")
    assert "Mitte (30,0 %) 20 von 20" in ev.verdict_predict(_ex(P_TWENTY))[1]


def test_eps_verdict_cases():
    kind, text = ev.verdict_eps(ev.eps_info(_t(P_FIVE)))
    assert kind == "warning" and text == ("Ein ε-Constraint-Entscheider (Zeitgrenze bei 40 % des Weges) ist auf 20 Instanzen in **10 von 20** Entscheidungen durch ein Gewicht erklärbar. "
                                          "Breite der erklärenden Menge im Median 14,0 Prozentpunkte. Ein lexikographischer Entscheider wird durch die Gewichte von 0 bis zum ersten Haltepunkt erklärt, "
                                          "Breite im Median 10,5 Prozentpunkte.")
    assert "**8 von 20**" in ev.verdict_eps(ev.eps_info(_t(P_EPS)))[1] and "**19 von 20**" in ev.verdict_eps(ev.eps_info(_t(P_SMALL)))[1]
    all_ok = {"frac": 40, "n": 20, "explained": 20, "point_only": 0, "widths": [10.0] * 20, "lex_widths": [5.0] * 20}
    assert ev.verdict_eps(all_ok)[0] == "info" and "**20 von 20**" in ev.verdict_eps(all_ok)[1]
    with_points = {**all_ok, "explained": 19, "point_only": 2}
    assert "(davon 2 nur an einem Haltepunkt)" in ev.verdict_eps(with_points)[1]


def test_units_verdict_cases():
    assert ev.verdict_units(ev.unit_info(ev.Settings()))[0] == "info"
    kind, text = ev.verdict_units(ev.unit_info(ev.Settings(**C.PRESETS[P_UNIT])))
    assert kind == "warning" and text == ("Mit der Zeit mal 10 erklärt dieselbe Entscheidung die Gewichte von 6,6 bis 100,0 % statt 41,6 bis 100,0 %: derselbe Plan, ein anderes Gewicht. "
                                          "Das Gewicht gilt nur in den Einheiten, in denen gerechnet wurde.")
