"""Zählungen über feste Instanzen (20 Versuche je 20 Instanzen, 8 Personen): die Zahlen aus der App und dem README, hier festgehalten."""

import zll_constants as C
import zll_evaluation as ev


def test_exact_sweep_contains_the_true_weight_every_time_and_shrinks_with_more_decisions(sweeps):
    s = sweeps["exact"]
    assert s["n_cases"] == 180 and all(s["per"][K]["contains"] == 180 for K in C.SWEEP_KS)
    medians = [s["per"][K]["width"][1] for K in C.SWEEP_KS]
    assert medians == sorted(medians, reverse=True)
    hits = [s["per"][K]["hits"] for K in C.SWEEP_KS]
    assert hits == sorted(hits)
    errs = [s["per"][K]["err"][1] for K in C.SWEEP_KS]
    assert errs == sorted(errs, reverse=True)


def test_exact_sweep_numbers(sweeps):
    s = sweeps["exact"]["per"]
    assert [round(s[K]["width"][1], 1) for K in C.SWEEP_KS] == [25.7, 14.4, 11.0, 6.3, 3.2, 1.7]
    assert [s[K]["within5"] for K in C.SWEEP_KS] == [2, 14, 29, 62, 128, 171]
    assert [round(s[K]["err"][1], 1) for K in C.SWEEP_KS] == [5.1, 3.2, 2.3, 1.5, 0.7, 0.3]
    assert [s[K]["hits"] for K in C.SWEEP_KS] == [2540, 2948, 3066, 3232, 3375, 3489] and all(s[K]["n_pred"] == 3600 for K in C.SWEEP_KS)


def test_exact_sweep_verdict(sweeps):
    kind, text = ev.verdict_exact_sweep(sweeps["exact"])
    assert kind == "info" and text.startswith("Exakter Entscheider, 180 Fälle (20 Versuche, neun Gewichte): K = 1: Breite Median 25,7") and text.endswith("Vorhersage richtig in 96,9 %.")


def test_noise_sweep_numbers(sweeps):
    s = sweeps["noise"]
    assert (s["single_unexplained"], s["single_n"]) == (518, 3600)
    assert [s["per"][K]["nonempty"] for K in C.SWEEP_KS] == [148, 117, 92, 56, 9, 0]
    assert [s["per"][K]["err_fit"][1] for K in C.SWEEP_KS] == [10.0, 6.0, 4.5, 3.0, 2.0, 1.0]
    assert [s["per"][K]["hits_fit"] for K in C.SWEEP_KS] == [1926, 2442, 2657, 2920, 3167, 3302]
    assert s["per"][20]["width"] is None and s["per"][20]["err"] is None


def test_noise_sweep_set_runs_empty_while_the_fit_keeps_improving(sweeps):
    s = sweeps["noise"]["per"]
    ne = [s[K]["nonempty"] for K in C.SWEEP_KS]
    assert ne == sorted(ne, reverse=True) and ne[-1] == 0
    fit = [s[K]["err_fit"][1] for K in C.SWEEP_KS]
    assert fit == sorted(fit, reverse=True)


def test_noise_sweep_verdict(sweeps):
    kind, text = ev.verdict_noise_sweep(sweeps["noise"])
    assert kind == "info" and "in 518 von 3600 (14,4 %)" in text and "K = 20: Menge nichtleer in 0 von 180, robuste Anpassung Fehler Median 1 Prozentpunkte, Vorhersage richtig in 91,7 %." in text


def test_eps_sweep_numbers(sweeps):
    s = sweeps["eps"]
    assert [(f, v["explained"], v["n"], v["point_only"]) for f, v in s["eps"].items()] == [(20, 209, 400, 0), (40, 206, 400, 0), (60, 221, 400, 1)]
    assert [round(v["width"], 1) for v in s["eps"].values()] == [17.4, 16.1, 16.6]
    assert tuple(round(x, 1) for x in s["lex"]) == (0.7, 14.4, 80.6)


def test_eps_sweep_explains_about_half(sweeps):
    for v in sweeps["eps"]["eps"].values():
        assert 0.4 < v["explained"] / v["n"] < 0.7


def test_eps_sweep_verdict(sweeps):
    kind, text = ev.verdict_eps_sweep(sweeps["eps"])
    assert kind == "info" and "Zeitgrenze 40 %: erklärbar in 206 von 400 (51,5 %), nur an einem Haltepunkt 0, Breite Median 16,1" in text and "0,7 / 14,4 / 80,6 Prozentpunkte" in text


def test_units_sweep(sweeps):
    assert sweeps["units"] == {"changed": 20, "same_corners": 20, "n": 20}
    kind, text = ev.verdict_units_sweep(sweeps["units"])
    assert kind == "warning" and "**20 von 20**" in text and "bleibt in 20 von 20 dieselbe" in text


def test_exact_sweep_maxima_and_regrets(sweeps):
    s = sweeps["exact"]["per"]
    assert [round(s[K]["width"][2], 1) for K in C.SWEEP_KS] == [76.3, 47.6, 33.0, 20.7, 15.2, 9.7]
    assert [round(s[K]["err"][2], 1) for K in C.SWEEP_KS] == [31.9, 16.0, 16.0, 9.2, 6.3, 3.5]
    assert [round(s[K]["regret"][1] * 100, 1) for K in C.SWEEP_KS] == [31.6, 11.1, 11.1, 7.8, 3.9, 2.0] and all(s[K]["regret"][0] == 0 for K in C.SWEEP_KS)
    assert [round(s[K]["hits"] / s[K]["n_pred"] * 100, 1) for K in C.SWEEP_KS] == [70.6, 81.9, 85.2, 89.8, 93.8, 96.9]


def test_noise_sweep_widths_maxima_and_fit_predictions(sweeps):
    s = sweeps["noise"]["per"]
    assert [round(s[K]["width"], 1) for K in C.SWEEP_KS[:-1]] == [27.3, 14.0, 9.0, 6.2, 1.9]
    assert [s[K]["err_fit"][2] for K in C.SWEEP_KS] == [66.0, 48.0, 23.0, 17.0, 17.0, 9.0]
    assert [round(s[K]["hits_fit"] / s[K]["n_pred"] * 100, 1) for K in C.SWEEP_KS] == [53.5, 67.8, 73.8, 81.1, 88.0, 91.7]
