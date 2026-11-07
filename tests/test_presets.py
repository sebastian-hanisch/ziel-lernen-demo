"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, und was jedes Preset zeigen soll."""

import zll_constants as C
import zll_evaluation as ev
import zll_presets as P

(P_FIVE, P_ONE, P_TWENTY, P_EMPTY, P_SPLIT, P_EPS, P_UNIT, P_SMALL) = list(C.PRESETS)


def _t(name):
    return ev.trial(ev.Settings(**C.PRESETS[name]))


def _ex(name):
    return ev.explain(_t(name))


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_slider_bounds():
    for preset in C.PRESETS.values():
        assert C.N_MIN <= preset["n"] <= C.N_MAX and 0 <= preset["seed"] <= C.SEED_MAX and C.W_MIN <= preset["w"] <= C.W_MAX and C.K_MIN <= preset["k"] <= C.K_MAX
        assert C.A_MIN <= preset["a"] <= C.A_MAX and C.FRAC_MIN <= preset["frac"] <= C.FRAC_MAX and preset["frac"] % C.FRAC_STEP == 0 and 0 <= preset["unit"] < len(C.UNITS)


def test_default_preset_equals_the_default_settings():
    assert ev.Settings(**C.PRESETS[P_FIVE]) == ev.Settings()


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)


def test_no_non_default_preset_equals_the_default_settings():
    """Lehre aus Stück 4: ein Preset, das den Voreinstellungen gleicht, wäre nicht von „nichts geklickt“ zu unterscheiden."""
    for name, preset in C.PRESETS.items():
        if name != P_FIVE:
            assert ev.Settings(**preset) != ev.Settings(), name
    assert len({tuple(sorted(p.items())) for p in C.PRESETS.values()}) == len(C.PRESETS)


def test_main_preset_leaves_a_narrow_interval_open():
    ex = _ex(P_FIVE)
    assert (round(ex["lo"], 1), round(ex["hi"], 1), round(ex["width"], 1), round(ex["mid"], 1), ex["pred_mid"]["hits"]) == (35.8, 41.7, 5.9, 38.8, 19) and ex["contains"]
    assert ex["pred_mid"]["n_wrong"] == 1 and round(ex["pred_mid"]["regret_median"] * 100, 2) == 0.14 == round(ex["pred_mid"]["regret_max"] * 100, 2)      # Median über den einen falschen Plan


def test_one_decision_preset_is_wide_and_the_midpoint_predicts_badly():
    ex = _ex(P_ONE)
    assert (round(ex["lo"], 1), ex["hi"], round(ex["width"], 1), round(ex["mid"], 1), ex["pred_mid"]["hits"], ex["pred_fit"]["hits"], ex["g_fit"]) == (57.5, 100.0, 42.5, 78.8, 7, 19, 58)


def test_twenty_preset_is_narrow_and_perfect():
    ex = _ex(P_TWENTY)
    assert (round(ex["lo"], 1), round(ex["hi"], 1), round(ex["width"], 1), ex["pred_mid"]["hits"]) == (29.4, 30.7, 1.3, 20)


def test_empty_preset_has_two_single_failures_and_a_fit_off_by_five():
    ex = _ex(P_EMPTY)
    assert ex["inter"] is None and ex["unexplained"] == 2 and ex["g_fit"] == 15 and ex["err_fit"] == 5 and ex["pred_fit"]["hits"] == 19


def test_split_preset_has_no_single_failure_but_an_empty_set_and_an_exact_fit():
    ex = _ex(P_SPLIT)
    assert ex["inter"] is None and ex["unexplained"] == 0 and ex["g_fit"] == 70 and ex["err_fit"] == 0 and ex["pred_fit"]["hits"] == 20


def test_eps_preset_is_explained_in_eight_of_twenty():
    info = ev.eps_info(_t(P_EPS))
    assert (info["explained"], info["n"], round(sorted(info["widths"])[len(info["widths"]) // 2], 1) > 0) == (8, 20, True)


def test_unit_preset_changes_the_interval_from_41_6_to_6_6():
    u = ev.unit_info(ev.Settings(**C.PRESETS[P_UNIT]))
    assert u["factor"] == 10 and u["changed"] and (round(float(u["interval"][0]) * 100, 1), round(float(u["interval_scaled"][0]) * 100, 1)) == (41.6, 6.6)


def test_small_preset_has_six_plans_and_a_wide_interval():
    ex = _ex(P_SMALL)
    assert ex["n"] == 3 and (round(ex["lo"], 1), round(ex["hi"], 1)) == (42.1, 62.6) and ev.eps_info(_t(P_SMALL))["explained"] == 19


def test_one_decision_preset_midpoint_is_18_8_points_off():
    assert round(_ex(P_ONE)["err_mid"], 1) == 18.8
