"""Der Entscheider, die Rückrechnung (exakt und robust), die Vorhersage, andere Entscheider, Einheiten, Zählungen über feste Instanzen und Verdikte (reine Funktionen: Art, Text; jede Zahl im Text kommt aus der Rechnung).

Gefragt wird: Welche Gewichte erklären beobachtete Entscheidungen? Ein Entscheider mit verborgenem Gewicht w* wählt auf K Instanzen (Seed + j) den für ihn besten Plan; gesucht ist das Gewicht. Exakt ist die erklärende Menge die
Schnittmenge der Intervalle, in denen der jeweils gewählte Plan optimal ist; bei verrauschten Entscheidungen wird sie mit mehr Entscheidungen immer häufiger leer, dann hilft die Anpassung mit der kleinsten Regret-Summe."""

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache

import numpy as np

import zll_algorithm as A
import zll_constants as C
import zll_scenario as S


def de(x: float, digits: int = 1) -> str:
    text = f"{x:.{digits}f}"
    if float(text) == 0.0:
        text = f"{0.0:.{digits}f}"
    return text.replace(".", ",")


def pct(x: float, digits: int = 1) -> str:
    return de(x * 100.0, digits) + " %"


def pp(x: float, digits: int = 1) -> str:
    """Prozentpunkte der Gewichtsachse."""
    return de(x, digits)


@dataclass(frozen=True)
class Settings:
    n: int = C.DEFAULT_N
    seed: int = C.DEFAULT_SEED
    w: int = C.DEFAULT_W
    k: int = C.DEFAULT_K
    a: int = C.DEFAULT_A
    frac: int = C.DEFAULT_FRAC
    unit: int = C.DEFAULT_UNIT


@dataclass
class Trial:
    """Ein Versuch: die 20 Entscheidungen auf den Instanzen Seed + j und die 20 Test-Instanzen (nur die Hüllen bleiben im Speicher)."""
    settings: Settings
    decisions: list          # je Entscheidung: Seed, Hülle, Haltepunkte, beobachteter Plan, Punkt, Intervall, Ecke des Entscheiders, ε-Wahl je Zeitgrenze, lexikographisches Intervall
    tests: list              # je Test-Instanz (Hülle, Haltepunkte)


def _decide(c1: np.ndarray, c2: np.ndarray, w: int, a: int, seed: int) -> dict:
    """Eine Entscheidung auf der Instanz (c1, c2): der Entscheider wählt mit seinen (verrauschten) Kosten den für ihn besten Plan beim Gewicht w; erklärt wird mit den wahren Kosten."""
    true = A.build_pair(c1, c2)
    dec = true if a == 0 else A.build_pair(*S.estimate_pair(c1, c2, a, seed))
    kd = A.corner_at(dec.hull, dec.bps, Fraction(w, 100))
    idx = dec.hull[kd][2]
    point = (int(true.s1[idx]), int(true.s2[idx]))
    eps = {}
    for f in range(C.FRAC_MIN, C.FRAC_MAX + 1, C.FRAC_STEP):
        e = A.eps_choice(true.s1, true.s2, f)
        pe = (int(true.s1[e]), int(true.s2[e]))
        eps[f] = {"idx": e, "point": pe, "interval": A.explain_interval(true.hull, true.bps, pe)}
    return {"seed": seed, "hull": true.hull, "bps": true.bps, "idx": idx, "plan": A.perms(c1.shape[0])[idx], "point": point, "interval": A.explain_interval(true.hull, true.bps, point), "corner_dec": kd,
            "eps": eps, "lex": A.interval_of_corner(true.bps, 0)}


@lru_cache(maxsize=None)
def _trial_cached(n: int, seed: int, w: int, a: int) -> tuple:
    decisions = [_decide(*S.make_pair(n, seed + j), w, a, seed + j) for j in range(C.K_MAX)]
    tests = []
    for j in range(C.N_TEST):
        pair = A.build_pair(*S.make_pair(n, seed + C.TEST_OFFSET + j))
        tests.append((pair.hull, pair.bps))
    return tuple(decisions), tuple(tests)


def trial(settings: Settings) -> Trial:
    d, t = _trial_cached(settings.n, settings.seed, settings.w, settings.a)
    return Trial(settings, list(d), list(t))


def _predict(tests: list, weight: Fraction, w: int) -> dict:
    """Vorhersage auf den Test-Instanzen: der Plan beim geschätzten Gewicht gegen den Plan beim wahren Gewicht (w in ganzen Prozent)."""
    hits, regrets, wrong = 0, [], []
    for hull, bps in tests:
        kp, kt = A.corner_at(hull, bps, weight), A.corner_at(hull, bps, Fraction(w, 100))
        hits += kp == kt
        pt = (hull[kp][0], hull[kp][1])
        r = float(A.regret(hull, pt, w))
        regrets.append(r)
        if kp != kt:
            wrong.append(r)      # falsch heißt: eine andere Ecke als beim wahren Gewicht (bei einem Gleichstand kann der Regret trotzdem 0 sein)
    # Median nur über die falschen Pläne (richtige haben Regret 0 und gehören nicht dazu); ohne falschen Plan: 0
    return {"hits": hits, "n": len(tests), "n_wrong": len(wrong), "regret_median": float(np.median(wrong)) if wrong else 0.0, "regret_max": float(max(regrets)), "regrets": regrets, "wrong_regrets": wrong}


def explain(t: Trial) -> dict:
    """Die Rückrechnung nach den ersten k Entscheidungen: Intervalle, Schnittmenge, Mitte, robuste Anpassung, Vorhersage."""
    s = t.settings
    ds = t.decisions[:s.k]
    intervals = [d["interval"] for d in ds]
    inter = A.intersect(intervals)
    rows = A.regret_rows([d["point"] for d in ds], [d["hull"] for d in ds])
    g_hat, sums = A.fit_rows(rows, s.k)
    out = {"n": s.n, "k": s.k, "w": s.w, "a": s.a, "decisions": ds, "intervals": intervals, "unexplained": sum(i is None for i in intervals), "inter": inter,
           "g_fit": g_hat, "fit_sums": [float(x) for x in sums], "err_fit": abs(g_hat - s.w), "pred_fit": _predict(t.tests, Fraction(g_hat, 100), s.w)}
    if inter is not None:
        lo, hi = inter
        mid = (lo + hi) / 2
        out.update({"lo": float(lo) * 100, "hi": float(hi) * 100, "width": float(hi - lo) * 100, "contains": lo <= Fraction(s.w, 100) <= hi, "mid": float(mid) * 100, "err_mid": abs(float(mid) * 100 - s.w),
                    "pred_mid": _predict(t.tests, mid, s.w)})
    return out


def eps_info(t: Trial) -> dict:
    """Ein ε-Constraint-Entscheider auf den 20 Instanzen dieses Versuchs: wie viele seiner Entscheidungen erklärt irgendein Gewicht? Dazu der lexikographische Entscheider."""
    f = t.settings.frac
    ivs = [d["eps"][f]["interval"] for d in t.decisions]
    ex = [i for i in ivs if i is not None]
    lex = [float(d["lex"][1] - d["lex"][0]) * 100 for d in t.decisions]
    return {"frac": f, "n": len(ivs), "explained": len(ex), "point_only": sum(i[0] == i[1] for i in ex), "widths": [float(i[1] - i[0]) * 100 for i in ex], "lex_widths": lex}


def unit_info(settings: Settings) -> dict:
    """Dieselbe Entscheidung in anderer Einheit: die Zeit mal f. Der gewählte Plan bleibt, sein Intervall ändert sich."""
    f = C.UNITS[settings.unit]
    c1, c2 = S.make_pair(settings.n, settings.seed)
    d = _decide(c1, c2, settings.w, settings.a, settings.seed)
    scaled = A.build_pair(c1, c2 * f)
    pt = (int(scaled.s1[d["idx"]]), int(scaled.s2[d["idx"]]))
    iv = A.explain_interval(scaled.hull, scaled.bps, pt)
    return {"factor": f, "interval": d["interval"], "interval_scaled": iv, "same_corners": {c[2] for c in d["hull"]} == {c[2] for c in scaled.hull}, "changed": iv != d["interval"]}


# --- Zählungen --------------------------------------------------------------------------------------------------------------------------------

@lru_cache(maxsize=None)
def _hull_of(n: int, seed: int) -> tuple:
    pair = A.build_pair(*S.make_pair(n, seed))
    return tuple(pair.hull), tuple(pair.bps)


def _q3(vals) -> tuple[float, float, float]:
    v = np.asarray(list(vals), dtype=float)
    return (float(v.min()), float(np.median(v)), float(v.max())) if len(v) else (0.0, 0.0, 0.0)


def sweep_exact() -> dict:
    """Je Versuch (20) und verborgenem Gewicht (neun): der exakte Entscheider; Breite, Fehler der Mitte und Vorhersage nach K Entscheidungen."""
    cases = []
    for t in range(C.SWEEP_TRIALS):
        base = C.SWEEP_BASE + t * C.SWEEP_PER_TRIAL
        hulls = [_hull_of(C.SWEEP_N, base + j) for j in range(C.SWEEP_PER_TRIAL)]
        tests = [_hull_of(C.SWEEP_N, base + C.TEST_OFFSET + j) for j in range(C.N_TEST)]
        for w in C.SWEEP_WS:
            ivs = [A.interval_of_corner(b, A.corner_at(h, b, Fraction(w, 100))) for h, b in hulls]
            case = {}
            for K in C.SWEEP_KS:
                lo, hi = A.intersect(ivs[:K])
                mid = (lo + hi) / 2
                pred = _predict(tests, mid, w)
                case[K] = {"width": float(hi - lo) * 100, "err": abs(float(mid) * 100 - w), "contains": lo <= Fraction(w, 100) <= hi, "hits": pred["hits"], "regrets": pred["regrets"], "wrong_regrets": pred["wrong_regrets"]}
            cases.append(case)
    return {"cases": cases}


def summary_exact(res: dict) -> dict:
    cs = res["cases"]
    out = {"n_cases": len(cs), "per": {}}
    for K in C.SWEEP_KS:
        w = [c[K]["width"] for c in cs]
        hits = sum(c[K]["hits"] for c in cs)
        reg = [r for c in cs for r in c[K]["regrets"]]
        wrong = [r for c in cs for r in c[K]["wrong_regrets"]]
        out["per"][K] = {"width": _q3(w), "within5": sum(x <= 5 for x in w), "err": _q3(c[K]["err"] for c in cs), "hits": hits, "n_pred": len(cs) * C.N_TEST, "n_wrong": len(wrong), "regret": (float(np.median(wrong)) if wrong else 0.0, float(max(reg))),
                         "contains": sum(c[K]["contains"] for c in cs)}
    return out


def sweep_noise() -> dict:
    """Der verrauschte Entscheider (Schätzfehler ±a): einzelne Entscheidungen, Schnittmenge nach K Entscheidungen und robuste Anpassung."""
    cases, single_un, single_n = [], 0, 0
    for t in range(C.SWEEP_TRIALS):
        base = C.SWEEP_BASE + t * C.SWEEP_PER_TRIAL
        hulls = [_hull_of(C.SWEEP_N, base + j) for j in range(C.SWEEP_PER_TRIAL)]
        tests = [_hull_of(C.SWEEP_N, base + C.TEST_OFFSET + j) for j in range(C.N_TEST)]
        decs = [S.make_pair(C.SWEEP_N, base + j) for j in range(C.SWEEP_PER_TRIAL)]
        trues = [A.build_pair(*p) for p in decs]
        noisy = [A.build_pair(*S.estimate_pair(*p, C.SWEEP_A, base + j)) for j, p in enumerate(decs)]
        for w in C.SWEEP_WS:
            ivs, pts = [], []
            for tr, nz in zip(trues, noisy):
                idx = nz.hull[A.corner_at(nz.hull, nz.bps, Fraction(w, 100))][2]
                pt = (int(tr.s1[idx]), int(tr.s2[idx]))
                pts.append(pt)
                ivs.append(A.explain_interval(tr.hull, tr.bps, pt))
            single_n += len(ivs)
            single_un += sum(i is None for i in ivs)
            rows = A.regret_rows(pts, [tr.hull for tr in trues])
            case = {}
            for K in C.SWEEP_KS:
                inter = A.intersect(ivs[:K])
                g_hat, _ = A.fit_rows(rows, K)
                fit_pred = _predict(tests, Fraction(g_hat, 100), w)
                entry = {"nonempty": inter is not None, "err_fit": abs(g_hat - w), "hits_fit": fit_pred["hits"]}
                if inter is not None:
                    entry.update({"width": float(inter[1] - inter[0]) * 100, "err": abs(float((inter[0] + inter[1]) / 2) * 100 - w)})
                case[K] = entry
            cases.append(case)
    return {"cases": cases, "single_unexplained": single_un, "single_n": single_n}


def summary_noise(res: dict) -> dict:
    cs = res["cases"]
    out = {"n_cases": len(cs), "single_unexplained": res["single_unexplained"], "single_n": res["single_n"], "per": {}}
    for K in C.SWEEP_KS:
        ne = [c[K] for c in cs if c[K]["nonempty"]]
        out["per"][K] = {"nonempty": len(ne), "width": float(np.median([e["width"] for e in ne])) if ne else None, "err": _q3(e["err"] for e in ne) if ne else None,
                         "err_fit": _q3(c[K]["err_fit"] for c in cs), "hits_fit": sum(c[K]["hits_fit"] for c in cs), "n_pred": len(cs) * C.N_TEST}
    return out


def sweep_eps() -> dict:
    """Der ε-Constraint-Entscheider und der lexikographische auf 400 Instanzen."""
    out = {f: {"explained": 0, "point_only": 0, "widths": [], "n": 0} for f in C.SWEEP_FRACS}
    lex = []
    for i in range(C.SWEEP_TRIALS * C.SWEEP_PER_TRIAL):
        pair = A.build_pair(*S.make_pair(C.SWEEP_N, C.SWEEP_BASE + i))
        lex.append(float(A.interval_of_corner(pair.bps, 0)[1]) * 100)
        for f in C.SWEEP_FRACS:
            e = A.eps_choice(pair.s1, pair.s2, f)
            iv = A.explain_interval(pair.hull, pair.bps, (int(pair.s1[e]), int(pair.s2[e])))
            out[f]["n"] += 1
            if iv is not None:
                out[f]["explained"] += 1
                out[f]["point_only"] += iv[0] == iv[1]
                out[f]["widths"].append(float(iv[1] - iv[0]) * 100)
    return {"eps": out, "lex": lex}


def summary_eps(res: dict) -> dict:
    return {"eps": {f: {"explained": v["explained"], "n": v["n"], "point_only": v["point_only"], "width": float(np.median(v["widths"])) if v["widths"] else None} for f, v in res["eps"].items()}, "lex": _q3(res["lex"])}


def sweep_units(seeds=range(C.SWEEP_BASE, C.SWEEP_BASE + 20)) -> dict:
    """Zeit mal 10: das Intervall des bei w = 0,5 gewählten Plans ändert sich, die Menge der Ecken nicht."""
    changed = same = 0
    for sd in seeds:
        u = unit_info(Settings(C.SWEEP_N, sd, 50, 1, 0, 0, C.UNITS.index(10)))
        changed += u["changed"]
        same += u["same_corners"]
    return {"changed": changed, "same_corners": same, "n": len(list(seeds))}


# --- Verdikte -------------------------------------------------------------------------------------------------------------------------------------

def verdict_explain(ex: dict) -> tuple[str, str]:
    k, w = ex["k"], ex["w"]
    if ex["inter"] is None:
        why = f" ({ex['unexplained']} davon schon einzeln nicht)" if ex["unexplained"] else ""
        return "warning", (f"**Kein Gewicht erklärt alle {k} {'Entscheidung' if k == 1 else 'Entscheidungen'}**{why}. Die robuste Anpassung (kleinste Summe der Regrets) wählt {ex['g_fit']} % gegen das wahre Gewicht {w} % "
                           f"(Fehler {ex['err_fit']} Prozentpunkte).")
    inside = "liegt darin" if ex["contains"] else "liegt **nicht** darin"
    return "info", (f"Nach {k} {'Entscheidung' if k == 1 else 'Entscheidungen'} erklären die Gewichte von {pp(ex['lo'])} bis {pp(ex['hi'])} % alle Entscheidungen (Breite **{pp(ex['width'])} Prozentpunkte**); "
                    f"das wahre Gewicht {w} % {inside}, die Mitte {pp(ex['mid'])} % liegt {pp(ex['err_mid'])} Prozentpunkte daneben.")


def _wrong_regret(p: dict) -> str:
    """Der Regret der falschen Pläne (nur diese zählen); ohne falschen Plan steht dort, dass keiner falsch ist."""
    if p["n_wrong"] == 0:
        return "kein Plan falsch"
    return f"Regret der falschen Pläne im Median {pct(p['regret_median'])}, höchstens {pct(p['regret_max'])}"


def verdict_predict(ex: dict) -> tuple[str, str]:
    f = ex["pred_fit"]
    fit = f"die robuste Anpassung ({ex['g_fit']} %) {f['hits']} von {f['n']}"
    if "pred_mid" not in ex:
        return "info", f"Auf {f['n']} neuen Instanzen sagt {fit} Plänen richtig voraus ({_wrong_regret(f)}); die Mitte gibt es nicht, die Menge ist leer."
    m = ex["pred_mid"]
    return "info", (f"Auf {m['n']} neuen Instanzen sagt die Mitte ({pp(ex['mid'])} %) {m['hits']} von {m['n']} Plänen richtig voraus ({_wrong_regret(m)}), "
                    f"{fit} Plänen.")


def verdict_eps(info: dict) -> tuple[str, str]:
    ex, n = info["explained"], info["n"]
    lex = _q3(info["lex_widths"])
    w = f" Breite der erklärenden Menge im Median {pp(float(np.median(info['widths'])))} Prozentpunkte." if info["widths"] else ""
    kind = "warning" if ex < n else "info"
    return kind, (f"Ein ε-Constraint-Entscheider (Zeitgrenze bei {info['frac']} % des Weges) ist auf {n} Instanzen in **{ex} von {n}** Entscheidungen durch ein Gewicht erklärbar"
                  f"{' (davon ' + str(info['point_only']) + ' nur an einem Haltepunkt)' if info['point_only'] else ''}.{w} Ein lexikographischer Entscheider wird durch die Gewichte von 0 bis zum ersten Haltepunkt erklärt, "
                  f"Breite im Median {pp(lex[1])} Prozentpunkte.")


def verdict_units(u: dict) -> tuple[str, str]:
    if u["factor"] == 1:
        return "info", "Ohne Umrechnung (Faktor 1) gelten die Intervalle der Rechnung; wähle einen anderen Faktor, um zu sehen, wie sich das Gewicht mit der Einheit ändert."
    lo0, hi0 = u["interval"]
    lo1, hi1 = u["interval_scaled"]
    return "warning", (f"Mit der Zeit mal {u['factor']} erklärt dieselbe Entscheidung die Gewichte von {pp(float(lo1) * 100)} bis {pp(float(hi1) * 100)} % statt {pp(float(lo0) * 100)} bis {pp(float(hi0) * 100)} %: "
                       f"derselbe Plan, ein anderes Gewicht. Das Gewicht gilt nur in den Einheiten, in denen gerechnet wurde.")


def verdict_exact_sweep(s: dict) -> tuple[str, str]:
    cells = "; ".join(f"K = {K}: Breite Median {pp(s['per'][K]['width'][1])} (höchstens 5 Prozentpunkte in {s['per'][K]['within5']} von {s['n_cases']}), Fehler der Mitte Median {pp(s['per'][K]['err'][1])}, "
                      f"Vorhersage richtig in {pct(s['per'][K]['hits'] / s['per'][K]['n_pred'])}" for K in C.SWEEP_KS)
    return "info", f"Exakter Entscheider, {s['n_cases']} Fälle (20 Versuche, neun Gewichte): {cells}."


def verdict_noise_sweep(s: dict) -> tuple[str, str]:
    cells = "; ".join(f"K = {K}: Menge nichtleer in {s['per'][K]['nonempty']} von {s['n_cases']}, robuste Anpassung Fehler Median {pp(s['per'][K]['err_fit'][1], 0)} Prozentpunkte, Vorhersage richtig in {pct(s['per'][K]['hits_fit'] / s['per'][K]['n_pred'])}"
                      for K in C.SWEEP_KS)
    return "info", (f"Verrauschter Entscheider (±{C.SWEEP_A}): eine einzelne Entscheidung ist für kein Gewicht erklärbar in {s['single_unexplained']} von {s['single_n']} ({pct(s['single_unexplained'] / s['single_n'])}); {cells}.")


def verdict_eps_sweep(s: dict) -> tuple[str, str]:
    cells = "; ".join(f"Zeitgrenze {f} %: erklärbar in {v['explained']} von {v['n']} ({pct(v['explained'] / v['n'])}), nur an einem Haltepunkt {v['point_only']}, Breite Median {pp(v['width'])}" for f, v in s["eps"].items())
    return "info", f"ε-Constraint-Entscheider: {cells}. Lexikographischer Entscheider: erklärende Gewichte 0 bis zum ersten Haltepunkt, Breite (Minimum / Median / Maximum) {pp(s['lex'][0])} / {pp(s['lex'][1])} / {pp(s['lex'][2])} Prozentpunkte."


def verdict_units_sweep(s: dict) -> tuple[str, str]:
    return "warning", (f"Zeit mal 10 auf {s['n']} festen Instanzen ({C.SWEEP_N} Personen, verborgenes Gewicht 50 %): das erklärende Intervall der Entscheidung ändert sich in **{s['changed']} von {s['n']}**, "
                       f"die Menge der Pläne, die ein Gewicht überhaupt wählen kann, bleibt in {s['same_corners']} von {s['n']} dieselbe.")
