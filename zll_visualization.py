"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import plotly.graph_objects as go

import zll_constants as C


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=360):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation="h", y=-0.25), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def _pct(iv):
    return float(iv[0]) * 100, float(iv[1]) * 100


def build_intervals(ex: dict):
    """Je Entscheidung die Gewichte, die sie erklären (Balken, ein Punkt an einem Haltepunkt, ein Kreuz bei „kein Gewicht“); die Schnittmenge ist grün hinterlegt, das wahre Gewicht und die Anpassung sind Linien."""
    fig = go.Figure()
    ys, labels = [], []
    for j, iv in enumerate(ex["intervals"]):
        label = f"Entscheidung {j + 1}"
        ys.append(label)
        labels.append(label)
        if iv is None:
            fig.add_trace(go.Scatter(x=[50], y=[label], mode="markers", marker=dict(symbol="x", size=11, color=C.COLOR_BAD), showlegend=False, hovertemplate=f"{label}: kein Gewicht erklärt sie<extra></extra>"))
            continue
        lo, hi = _pct(iv)
        if lo == hi:
            fig.add_trace(go.Scatter(x=[lo], y=[label], mode="markers", marker=dict(symbol="diamond", size=10, color=C.COLOR_BAR), showlegend=False, hovertemplate=f"{label}: nur das Gewicht %{{x:.1f}} %<extra></extra>"))
        else:
            fig.add_trace(go.Bar(x=[hi - lo], base=[lo], y=[label], orientation="h", marker_color=C.COLOR_BAR, showlegend=False, hovertemplate=f"{label}: {lo:.1f} bis {hi:.1f} %<extra></extra>"))
    if ex["inter"] is not None:
        lo, hi = ex["lo"], ex["hi"]
        fig.add_vrect(x0=lo, x1=max(hi, lo + 0.15), fillcolor=C.COLOR_SET, opacity=0.22, line_width=0)
    fig.add_vline(x=ex["w"], line_color=C.COLOR_TRUE, line_width=2, annotation_text=f"wahres Gewicht {ex['w']} %", annotation_position="top")
    if ex["inter"] is None:
        fig.add_vline(x=ex["g_fit"], line_color=C.COLOR_FIT, line_dash="dash", annotation_text=f"Anpassung {ex['g_fit']} %", annotation_position="bottom")
    fig.update_layout(barmode="overlay", showlegend=False)
    fig.update_xaxes(range=[0, 100], title_text="Gewicht der Zeit (%)")
    fig.update_yaxes(autorange="reversed", categoryorder="array", categoryarray=labels)
    return _base(fig, height=max(240, 34 * len(ex["intervals"]) + 90))


def build_fit_curve(ex: dict):
    """Summe der relativen Regrets der beobachteten Pläne je Gewicht: die robuste Anpassung ist das Minimum."""
    fig = go.Figure(go.Scatter(x=list(C.GRID), y=[v * 100 for v in ex["fit_sums"]], mode="lines", line=dict(color=C.COLOR_BAR), hovertemplate="Gewicht %{x} %: Regret-Summe %{y:.1f} %<extra></extra>", name="Summe der Regrets"))
    fig.add_vline(x=ex["g_fit"], line_color=C.COLOR_FIT, line_dash="dash", annotation_text=f"Minimum bei {ex['g_fit']} %", annotation_position="top")
    fig.add_vline(x=ex["w"], line_color=C.COLOR_TRUE, line_width=2, annotation_text=f"wahr {ex['w']} %", annotation_position="bottom")
    fig.update_xaxes(range=[0, 100], title_text="Angenommenes Gewicht der Zeit (%)")
    fig.update_yaxes(title_text="Summe der relativen Regrets (%)", rangemode="tozero")
    return _base(fig, height=300)


def build_eps(info: dict, decisions: list, frac: int):
    """Der Zeitgrenzen-Entscheider auf den 20 Instanzen: erklärende Gewichte je Instanz (ein Punkt: nur an einem Haltepunkt; rotes Kreuz: kein Gewicht)."""
    fig = go.Figure()
    for j, d in enumerate(decisions):
        label = f"{j + 1}"
        iv = d["eps"][frac]["interval"]
        if iv is None:
            fig.add_trace(go.Scatter(x=[50], y=[label], mode="markers", marker=dict(symbol="x", size=9, color=C.COLOR_BAD), showlegend=False, hovertemplate=f"Instanz {label}: kein Gewicht erklärt die Wahl<extra></extra>"))
            continue
        lo, hi = _pct(iv)
        if lo == hi:
            fig.add_trace(go.Scatter(x=[lo], y=[label], mode="markers", marker=dict(symbol="diamond", size=8, color=C.COLOR_BAR), showlegend=False, hovertemplate=f"Instanz {label}: nur das Gewicht %{{x:.1f}} %<extra></extra>"))
        else:
            fig.add_trace(go.Bar(x=[hi - lo], base=[lo], y=[label], orientation="h", marker_color=C.COLOR_BAR, showlegend=False, hovertemplate=f"Instanz {label}: {lo:.1f} bis {hi:.1f} %<extra></extra>"))
    fig.update_layout(barmode="overlay")
    fig.update_xaxes(range=[0, 100], title_text="Gewichte, die die Wahl erklären (%)")
    fig.update_yaxes(autorange="reversed", type="category", title_text="Instanz")
    return _base(fig, height=520)


def build_units(u: dict):
    """Dasselbe Intervall in der Einheit der Rechnung und in der umgerechneten Einheit."""
    fig = go.Figure()
    rows = [("Zeit ×1", u["interval"]), (f"Zeit ×{u['factor']}", u["interval_scaled"])]
    seen = []
    for label, iv in rows:
        if label in seen or iv is None:
            continue
        seen.append(label)
        lo, hi = _pct(iv)
        fig.add_trace(go.Bar(x=[max(hi - lo, 0.4)], base=[lo], y=[label], orientation="h", marker_color=C.COLOR_BAR if label == "Zeit ×1" else C.COLOR_FIT, showlegend=False,
                             hovertemplate=f"{label}: {lo:.1f} bis {hi:.1f} %<extra></extra>"))
    fig.update_layout(barmode="overlay")
    fig.update_xaxes(range=[0, 100], title_text="Gewichte, die die Entscheidung erklären (%)")
    fig.update_yaxes(autorange="reversed")
    return _base(fig, height=190)


def build_exact_sweep(s: dict):
    """Exakter Entscheider: Breite der erklärenden Menge (Median, Spanne) und Anteil richtiger Vorhersagen je Zahl der Entscheidungen."""
    ks = list(C.SWEEP_KS)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[str(k) for k in ks], y=[s["per"][k]["width"][2] for k in ks], mode="lines", line=dict(width=0), showlegend=False, hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=[str(k) for k in ks], y=[s["per"][k]["width"][0] for k in ks], mode="lines", line=dict(width=0), fill="tonexty", fillcolor="rgba(76,120,168,0.2)", name="Breite: kleinste bis größte", hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=[str(k) for k in ks], y=[s["per"][k]["width"][1] for k in ks], mode="lines+markers", line=dict(color=C.COLOR_BAR), name="Breite (Median, Prozentpunkte)",
                             hovertemplate="%{x} Entscheidungen: Breite im Median %{y:.1f} Prozentpunkte<extra></extra>"))
    fig.add_trace(go.Scatter(x=[str(k) for k in ks], y=[s["per"][k]["hits"] / s["per"][k]["n_pred"] * 100 for k in ks], mode="lines+markers", line=dict(color=C.COLOR_SET, dash="dash"), name="Vorhersage richtig (%)", yaxis="y2",
                             hovertemplate="%{x} Entscheidungen: Vorhersage richtig in %{y:.1f} %<extra></extra>"))
    fig.update_layout(yaxis2=dict(overlaying="y", side="right", range=[0, 100], title="Vorhersage richtig (%)", fixedrange=True))
    fig.update_xaxes(type="category", title_text="Zahl der beobachteten Entscheidungen")
    fig.update_yaxes(title_text="Breite (Prozentpunkte)", rangemode="tozero")
    return _base(fig, height=340)


def build_noise_sweep(s: dict):
    """Verrauschter Entscheider: in wie vielen Fällen die Schnittmenge noch nicht leer ist, und der Fehler der robusten Anpassung (Median)."""
    ks = list(C.SWEEP_KS)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=[str(k) for k in ks], y=[s["per"][k]["nonempty"] / s["n_cases"] * 100 for k in ks], marker_color=C.COLOR_BAR, name="Menge nicht leer (% der Fälle)",
                         hovertemplate="%{x} Entscheidungen: Menge nicht leer in %{y:.0f} % der Fälle<extra></extra>"))
    fig.add_trace(go.Scatter(x=[str(k) for k in ks], y=[s["per"][k]["err_fit"][1] for k in ks], mode="lines+markers", line=dict(color=C.COLOR_FIT, dash="dash"), name="Fehler der robusten Anpassung (Median, Prozentpunkte)", yaxis="y2",
                             hovertemplate="%{x} Entscheidungen: Fehler im Median %{y:.0f} Prozentpunkte<extra></extra>"))
    fig.update_layout(yaxis2=dict(overlaying="y", side="right", rangemode="tozero", title="Fehler (Prozentpunkte)", fixedrange=True))
    fig.update_xaxes(type="category", title_text="Zahl der beobachteten Entscheidungen")
    fig.update_yaxes(title_text="Fälle (%)", range=[0, 100])
    return _base(fig, height=340)


def build_eps_sweep(s: dict):
    """Anteil der Entscheidungen des Zeitgrenzen-Entscheiders, die irgendein Gewicht erklärt, je Zeitgrenze."""
    fr = list(s["eps"])
    fig = go.Figure(go.Bar(x=[f"{f} %" for f in fr], y=[s["eps"][f]["explained"] / s["eps"][f]["n"] * 100 for f in fr], marker_color=C.COLOR_BAR,
                           hovertemplate="Zeitgrenze %{x}: erklärbar in %{y:.1f} % der Entscheidungen<extra></extra>"))
    fig.update_xaxes(type="category", title_text="Zeitgrenze (Anteil des Weges von der besten Zeit zur Zeit des Kosten-Optimums)")
    fig.update_yaxes(title_text="Durch ein Gewicht erklärbar (%)", range=[0, 100])
    return _base(fig, height=300)
