"""PDF-Export der Rückrechnung (fpdf2). Kernschriften sind latin-1: Umlaute gehen, Sonderzeichen werden ersetzt."""

from __future__ import annotations

from fpdf import FPDF

import zll_constants as C
from zll_evaluation import Settings, de, eps_info, explain, pct, pp, trial, unit_info, verdict_eps, verdict_explain, verdict_predict, verdict_units

_REPLACE = {"→": "->", "–": "-", "—": "-", "−": "-", "≤": "<=", "≥": ">=", "·": "*", "×": "x", "„": '"', "“": '"', "²": "2", "ε": "eps", "∞": "unendlich"}


def _s(text) -> str:
    out = str(text).replace("**", "").replace("`", "")
    for old, new in _REPLACE.items():
        out = out.replace(old, new)
    return out.encode("latin-1", "replace").decode("latin-1")


def build_pdf(s: Settings) -> bytes:
    t = trial(s)
    ex = explain(t)
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 9, _s("Ziel aus Entscheidungen lernen"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 5, _s(f"{s.n} Personen, {s.n} Aufgaben, Seed {s.seed}; verborgenes Gewicht der Zeit {s.w} %, {s.k} beobachtete Entscheidungen, Schätzfehler des Entscheiders bis {s.a}. Alles simuliert."), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 6, _s("Erklärende Gewichte je Entscheidung"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    for j, iv in enumerate(ex["intervals"]):
        if iv is None:
            line = "kein Gewicht erklärt sie"
        elif iv[0] == iv[1]:
            line = f"nur das Gewicht {pp(float(iv[0]) * 100)} %"
        else:
            line = f"{pp(float(iv[0]) * 100)} bis {pp(float(iv[1]) * 100)} %"
        pdf.multi_cell(0, 5, _s(f"Entscheidung {j + 1}: {line}"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    for text in (verdict_explain(ex)[1], verdict_predict(ex)[1], verdict_eps(eps_info(t))[1], verdict_units(unit_info(s))[1]):
        pdf.multi_cell(0, 5, _s(text), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)
    pdf.ln(2)
    pdf.set_font("Helvetica", "I", 8)
    pdf.multi_cell(0, 4, _s("Bei Gleichstand gilt der kleinste Index der Aufzählung. Quelle: ziel-lernen-demo, Sebastian Hanisch."), new_x="LMARGIN", new_y="NEXT")
    return bytes(pdf.output())
