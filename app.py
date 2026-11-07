"""Ziel lernen - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Stück 12 der Reihe „Zielfunktionsdesign“: Kann man das Ziel aus den Entscheidungen zurückrechnen, die ein Entscheider getroffen hat?
Die Demo zeigt, welche Gewichte beobachtete Entscheidungen erklären (Schnittmenge von Intervallen), wie gut das Ergebnis neue Entscheidungen vorhersagt,
was bei Schätzfehlern und bei anderen Entscheidern (Zeitgrenze, Reihenfolge der Ziele) passiert und warum das Gewicht an die Einheit gebunden ist.

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import zll_constants as C
from zll_evaluation import (
    Settings,
    eps_info,
    explain,
    pp,
    summary_eps,
    summary_exact,
    summary_noise,
    sweep_eps,
    sweep_exact,
    sweep_noise,
    sweep_units,
    trial,
    unit_info,
    verdict_eps,
    verdict_eps_sweep,
    verdict_exact_sweep,
    verdict_explain,
    verdict_noise_sweep,
    verdict_predict,
    verdict_units,
    verdict_units_sweep,
)
from zll_layout import dunkles_design, kopf_css
from zll_pdf_export import build_pdf
from zll_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)
from zll_visualization import build_eps, build_eps_sweep, build_exact_sweep, build_fit_curve, build_intervals, build_noise_sweep, build_units

st.set_page_config(page_title="Ziel lernen – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner="Die Entscheidungen werden gerechnet ...")
def _trial_result(settings):
    t = trial(settings)
    return explain(t), eps_info(t), t.decisions


@st.cache_data(show_spinner=False)
def _unit(settings):
    return unit_info(settings)


@st.cache_data(show_spinner="400 feste Instanzen werden gerechnet (je 40 320 Pläne, neun Gewichte) ...")
def _sweep_exact():
    return summary_exact(sweep_exact())


@st.cache_data(show_spinner="400 feste Instanzen werden mit Schätzfehler gerechnet ...")
def _sweep_noise():
    return summary_noise(sweep_noise())


@st.cache_data(show_spinner="400 feste Instanzen werden gerechnet ...")
def _sweep_eps():
    return summary_eps(sweep_eps())


@st.cache_data(show_spinner="20 feste Instanzen werden in anderer Einheit gerechnet ...")
def _sweep_units():
    return sweep_units()


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in zll_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🔎 Ziel lernen")
st.markdown(
    """
**Kann man das Ziel zurückrechnen, wenn man nur die Entscheidungen sieht?** Ein Entscheider ordnet **n Personen** auf **n Aufgaben** zu und wägt dabei zwei Dinge ab: **Kosten** und **Zeit**. Sein **Gewicht der Zeit** kennen wir nicht,
wir sehen nur, welchen Plan er auf **K Instanzen** gewählt hat. Zu jeder Entscheidung gehört ein **Intervall von Gewichten**, bei denen genau dieser Plan der beste ist; **erklärt** wird sie von allen Gewichten im Schnitt der Intervalle.
Die Demo zeigt, wie schmal dieser Schnitt wird, was er über neue Entscheidungen verrät und wann die Rückrechnung versagt: bei **Schätzfehlern**, bei einem **anderen Entscheider** und bei einer **anderen Einheit**.

Weiter unten: **🔬 Die Vorhersage**, **🔬 Der Entscheider rechnet ungenau**, **🔬 Ein anderer Entscheider**, **🔬 Die Einheit**, **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So funktioniert die Rückrechnung", expanded=True):
    st.markdown(
        """
1. **Die Instanz:** Kosten und Zeit sind zwei Zahlentabellen (ganze Zahlen 11 bis 109). Der Entscheider minimiert **(1 − w) · Kosten + w · Zeit** mit seinem verborgenen Gewicht `w`; alle n! Pläne werden aufgezählt, bei Gleichstand gilt der kleinste Index.
2. **Ein Intervall je Entscheidung:** Ein Plan ist für einen **Bereich** von Gewichten optimal (eine Ecke der unteren konvexen Hülle der Punkte Kosten/Zeit), für **ein einziges** Gewicht (auf einer Kante) oder für **keines**.
3. **Die erklärende Menge:** der Schnitt der Intervalle aller beobachteten Entscheidungen; die **Mitte** ist die Schätzung. **Vorhersage:** auf 20 neuen Instanzen zählt, wie oft der Plan der Schätzung dem Plan des wahren Gewichts gleicht.
4. **Rauschen:** rechnet der Entscheider mit Schätzungen (jede Zahl um bis zu ±a verschoben), wird der Schnitt mit mehr Entscheidungen immer häufiger leer; die **robuste Anpassung** nimmt dann das Gewicht mit der kleinsten Summe der relativen Regrets.
5. **Messungen, kein Satz:** Alle Zahlen sind Zählungen an festen Instanzen dieses Zufallsmodells; sie sagen nichts über echte Entscheider.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Instanz**")
    n = st.slider("Personen und Aufgaben n", *bounds("n_slider"), key="n_slider", help="Alle n! Pläne werden aufgezählt (bis 40 320).")
    seed = st.number_input("Zufalls-Seed", *bounds("seed_input"), key="seed_input", step=1, help="Die Entscheidung j steht auf der Instanz mit dem Seed (Seed + j); die Test-Instanzen der Vorhersage bei Seed + 400 + j.")
    st.button("🎲 Neue Instanz generieren", width="stretch", on_click=randomize_seed)
    st.markdown("**Der Entscheider**")
    w = st.slider("Verborgenes Gewicht der Zeit in %", *bounds("w_slider"), key="w_slider", help="Der Entscheider minimiert (100 − w) · Kosten + w · Zeit. Das Gewicht kennt die Rückrechnung nicht.")
    k = st.slider("Beobachtete Entscheidungen K", *bounds("k_slider"), key="k_slider", help="Auf wie vielen Instanzen wir seine Wahl sehen.")
    a = st.slider("Schätzfehler des Entscheiders ±a", *bounds("a_slider"), key="a_slider", help="0: er rechnet exakt. Sonst ist jede Zahl der beiden Tabellen um eine ganze Zahl von −a bis +a verschoben (die Rückrechnung kennt die wahren Zahlen).")
    st.markdown("**Ein anderer Entscheider**")
    frac = st.slider("Zeitgrenze in % des Weges", *bounds("frac_slider"), key="frac_slider", step=C.FRAC_STEP,
                     help="Der Entscheider minimiert die Kosten unter einer Zeitgrenze: 0 % ist die beste erreichbare Zeit, 100 % die Zeit des Kosten-Optimums.")
    st.markdown("**Die Einheit**")
    unit = st.selectbox("Zeit rechnen mal", list(range(len(C.UNITS))), key="unit_select", format_func=lambda i: f"Faktor {C.UNITS[i]}" + (" (wie gerechnet)" if i == 0 else ""),
                        help="Die Zeit in einer anderen Einheit (Minuten statt Stunden): derselbe Entscheider, dieselben Pläne, ein anderes Gewicht.")

sync_query_params({"n_slider": int(n), "seed_input": int(seed), "w_slider": int(w), "k_slider": int(k), "a_slider": int(a), "frac_slider": int(frac), "unit_select": int(unit)})

settings = Settings(int(n), int(seed), int(w), int(k), int(a), int(frac), int(unit))
ex, einfo, decisions = _trial_result(settings)

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis: welche Gewichte erklären die Entscheidungen?")
m1, m2, m3 = st.columns(3)
if ex["inter"] is None:
    m1.metric("Erklärende Menge", "leer", delta=f"{ex['unexplained']} einzeln nicht erklärbar", delta_color="off")
    m2.metric("Robuste Anpassung", f"{ex['g_fit']} %", delta=f"Fehler {ex['err_fit']} Prozentpunkte", delta_color="off")
    m3.metric("Vorhersage richtig", f"{ex['pred_fit']['hits']} von {ex['pred_fit']['n']}", delta="mit der robusten Anpassung", delta_color="off")
else:
    m1.metric("Erklärende Menge", f"{pp(ex['lo'])}–{pp(ex['hi'])} %", delta=f"Breite {pp(ex['width'])} Prozentpunkte", delta_color="off")
    m2.metric("Mitte", f"{pp(ex['mid'])} %", delta=f"Fehler {pp(ex['err_mid'])} Prozentpunkte", delta_color="off")
    m3.metric("Vorhersage richtig", f"{ex['pred_mid']['hits']} von {ex['pred_mid']['n']}", delta="mit der Mitte", delta_color="off")
st.plotly_chart(build_intervals(ex), width="stretch", key="intervals_chart")
st.caption("Jede Zeile ist eine Entscheidung: der Balken zeigt die Gewichte, bei denen genau dieser Plan der beste ist (ein Punkt: nur ein einziges Gewicht; ein Kreuz: kein Gewicht). Grün hinterlegt der Schnitt, die goldene Linie das wahre Gewicht.")
st.download_button("📄 Rückrechnung als PDF", data=build_pdf(settings), file_name="ziel-lernen.pdf", mime="application/pdf", key="pdf_download")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Wie viel verraten die Entscheidungen über das Ziel?")
kind, text = verdict_explain(ex)
getattr(st, kind)(text)

st.markdown("---")

# --- Experimente ---------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Die Vorhersage")
st.caption("Die Schätzung wird auf 20 neuen Instanzen geprüft: stimmt der Plan beim geschätzten Gewicht mit dem Plan beim wahren Gewicht überein? Wenn nicht, wie viel schlechter ist er (relativer Regret beim wahren Gewicht)?")
kind, text = verdict_predict(ex)
getattr(st, kind)(text)
if st.toggle("Die Breite und die Vorhersage über feste Instanzen nachrechnen (je Zahl der Entscheidungen)", value=False, key="sweep_exact"):
    s = _sweep_exact()
    kind, text = verdict_exact_sweep(s)
    getattr(st, kind)(text)
    st.plotly_chart(build_exact_sweep(s), width="stretch", key="exact_chart")

st.markdown("---")

st.subheader("🔬 Der Entscheider rechnet ungenau")
st.caption("Rechnet der Entscheider mit geschätzten Zahlen, ist seine Wahl nicht mehr für jedes Gewicht eine Optimalwahl der wahren Zahlen, und der Schnitt wird mit mehr Entscheidungen immer häufiger leer. Die robuste Anpassung nimmt das Gewicht mit der kleinsten Summe der relativen Regrets (Kurve unten).")
st.plotly_chart(build_fit_curve(ex), width="stretch", key="fit_chart")
if settings.a == 0:
    st.info("Mit Schätzfehler 0 ist die Kurve für das wahre Gewicht null, wenn der Schnitt es enthält; erhöhe den Schätzfehler in der Seitenleiste, um den Schnitt zu verlieren.")
if st.toggle("Den Schätzfehler über feste Instanzen nachrechnen (±5, je Zahl der Entscheidungen)", value=False, key="sweep_noise"):
    s = _sweep_noise()
    kind, text = verdict_noise_sweep(s)
    getattr(st, kind)(text)
    st.plotly_chart(build_noise_sweep(s), width="stretch", key="noise_chart")

st.markdown("---")

st.subheader("🔬 Ein anderer Entscheider")
st.caption(f"Ein Entscheider, der die Kosten unter einer Zeitgrenze minimiert (Grenze bei {settings.frac} % des Weges von der besten Zeit zur Zeit des Kosten-Optimums), wählt oft Pläne, die kein Gewicht als beste Wahl ergibt. "
           "Die Abbildung zeigt seine 20 Entscheidungen auf den Instanzen dieses Versuchs: Balken sind erklärende Gewichte, ein Kreuz heißt, kein Gewicht erklärt die Wahl.")
st.plotly_chart(build_eps(einfo, decisions, settings.frac), width="stretch", key="eps_chart")
kind, text = verdict_eps(einfo)
getattr(st, kind)(text)
if st.toggle("Die Zeitgrenzen über feste Instanzen nachrechnen (20, 40 und 60 %)", value=False, key="sweep_eps"):
    s = _sweep_eps()
    kind, text = verdict_eps_sweep(s)
    getattr(st, kind)(text)
    st.plotly_chart(build_eps_sweep(s), width="stretch", key="eps_sweep_chart")

st.markdown("---")

st.subheader("🔬 Die Einheit")
st.caption("Rechnet man die Zeit in einer anderen Einheit, wählt derselbe Entscheider denselben Plan, aber das Gewicht, das ihn erklärt, ändert sich: ein Gewicht ist nur zusammen mit seinen Einheiten zu lesen. Gezeigt wird die erste Entscheidung.")
u = _unit(settings)
st.plotly_chart(build_units(u), width="stretch", key="units_chart")
kind, text = verdict_units(u)
getattr(st, kind)(text)
if st.toggle("Die Einheit über feste Instanzen nachrechnen (Zeit mal 10)", value=False, key="sweep_units"):
    kind, text = verdict_units_sweep(_sweep_units())
    getattr(st, kind)(text)

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Der Entscheider gewichtet linear** | Wählt er nach einer Zeitgrenze (ε-Constraint), erklärt ihn in etwa der Hälfte der Entscheidungen kein Gewicht, und die Rückrechnung findet dann ein Gewicht, das nichts erklärt; wählt er lexikographisch (Reihenfolge der Ziele), erklärt ihn ein kleines Gewicht mit breitem Intervall | – |
| **Die Tabellen sind bekannt** | Hier kennt die Rückrechnung die wahren Zahlen; sieht sie nur geschätzte, wird die erklärende Menge vermutlich zusätzlich verzerrt (Vermutung, nicht gemessen) | Stück 11 |
| **Genau zwei Ziele** | Bei mehr Zielen ist die erklärende Menge ein Gebiet, nicht ein Intervall; die Aufzählung der Pläne geht weiter, die Darstellung nicht | – |
| **Alle Pläne sind aufgezählt** | Bis 8 Personen (40 320 Pläne); bei großen Problemen braucht es einen Löser für die Hülle | Dokumentation des Lösers |
| **Das Gewicht gilt nur in seinen Einheiten** | In anderer Einheit erklärt derselbe Plan ein anderes Gewicht; vergleichbar sind nur Gewichte aus derselben Rechnung | – |
| **Der Entscheider bleibt derselbe** | Ändert er sein Gewicht oder reagiert er auf Anreize, sagt die Rückrechnung die Zukunft nicht voraus (Anreize und Mechanism Design sind nicht Teil der Demo) | – |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Problem.** Eine Instanz sind zwei ganzzahlige Matrizen $c^1, c^2 \in \mathbb{Z}^{n \times n}$ (Kosten, Zeit). Ein Plan ist eine Permutation $p$, seine Summen sind $s_1(p) = \sum_i c^1_{i,p(i)}$ und $s_2(p) = \sum_i c^2_{i,p(i)}$.
Der Entscheider mit Gewicht $w \in [0,1]$ minimiert $(1-w)\, s_1(p) + w\, s_2(p)$ (bei Gleichstand der kleinste Index).

**Intervall einer Entscheidung.** Die Pläne, die für ein Gewicht optimal sind, sind die Ecken der unteren konvexen Hülle der Punkte $(s_1, s_2)$. Mit den Haltepunkten $w_k = \frac{\Delta_1}{\Delta_1 + \Delta_2}$ zwischen zwei Ecken
ist die Ecke $k$ für $w \in [w_{k-1}, w_k]$ optimal; ein Plan auf einer Kante ist es nur für das eine Gewicht $w_k$, jeder andere nie.

**Erklärende Menge.** $W(x_1, \dots, x_K) = \bigcap_j I(x_j)$, die Mitte $\hat w = \tfrac12 (\min W + \max W)$. Leer, wenn die Entscheidungen nicht zu einem Gewicht passen (alles in exakten Brüchen).

**Robuste Anpassung.** Der relative Regret von $x$ beim Gewicht $g$ ist $r_j(g) = \dfrac{f_g(x_j) - \min_p f_g(p)}{\min_p f_g(p)}$; gewählt wird $\hat g = \arg\min_{g \in \{0, 1, \dots, 100\}\%} \sum_j r_j(g)$ (Gleichstand: das kleinere Gewicht).

**Einheit.** Die Zeit mal $f$ verschiebt die Haltepunkte zu $\frac{\Delta_1}{\Delta_1 + f\, \Delta_2}$; die Ecken bleiben dieselben.

**Literatur.** Keine Aussage dieser Demo stützt sich auf gelesene Literatur; alle Zahlen sind Messungen an dem Zufallsmodell der Demo.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zur Reihe: [Zielfunktionsdesign: das Ziel ist das Modell](https://sebastianhanisch.net/konzepte-zielfunktionsdesign.html)."
)
