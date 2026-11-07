# Ziel lernen – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-ziel-lernen-demo.streamlit.app/)** -->

Stück 12 der Linie **Zielfunktionsdesign** („Das Ziel ist das Modell“) in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“ (Arbeitsname; Name, Bereich und Themenfeld werden erst bei der Einbindung in die Website festgelegt). Es ist ein **gelbes** (optionales) Stück und baut auf Stück 3 (`zwei-kriterien-demo`), Stück 8 (`goodhart-kurve-demo`), Stück 11 (`planstabilitaet-demo`) und Stück 13 (`zielkarte-demo`) auf: dieselbe **Zuordnung** von n Personen auf n Aufgaben mit zwei Kriterien, Kosten und Zeit, aber in **umgekehrter Richtung**. Ein Entscheider hat ein **verborgenes Gewicht** der Zeit und trifft Entscheidungen; gesucht ist das Gewicht, das sie erklärt. Die Demo misst, **wie breit die Menge der erklärenden Gewichte ist, wie gut sie neue Entscheidungen vorhersagt, was bei Schätzfehlern oder einer anderen Entscheidungsregel passiert und warum ein Gewicht nur zusammen mit seinen Einheiten zu lesen ist**. Alles ist **simuliert**; keine Aussage über echte Entscheider, Pläne oder Betriebe.

## Warum dieses Problem

Wer ein Ziel nicht aufschreiben kann, gibt oft Beispiele: so hat die Disponentin entschieden, so der Einkäufer. Aus solchen Entscheidungen ein Ziel zurückzurechnen ist verlockend, aber heikel: ein Plan ist für einen **Bereich** von Gewichten optimal, nicht für eines; ein Entscheider rechnet mit Schätzungen und widerspricht sich dann selbst; er wägt vielleicht gar nicht mit einer Gewichtssumme ab; und das Gewicht hängt an den Einheiten, in denen gerechnet wurde. Die Fragen: Wie viel lassen k Entscheidungen offen? Reicht das, um die nächste vorherzusagen? Und wann findet die Rückrechnung ein Gewicht, das nichts erklärt?

## Modell

Gegeben `n` Personen und `n` Aufgaben, zwei Matrizen `c1` (Kosten) und `c2` (Zeit) aus ganzen Zahlen 11 bis 109; ein Plan ist eine Zuordnung (Permutation); **alle `n!` Pläne werden aufgezählt** (bis `8! = 40 320`), alles in ganzen Zahlen und exakten Brüchen. Der Entscheider mit **verborgenem Gewicht** `w` (Prozent) minimiert `(100 − w)·Kosten + w·Zeit` (bei Gleichstand der kleinste Index) auf K Instanzen mit den Seeds `Seed + j`. **Intervall einer Entscheidung:** die Gewichte, bei denen genau dieser Plan optimal ist: ein Bereich (Ecke der unteren konvexen Hülle der Punkte Kosten/Zeit), ein einziges Gewicht (Punkt auf einer Kante) oder keines. **Erklärende Menge:** der Schnitt der Intervalle aller K Entscheidungen, ihre **Mitte** ist die Schätzung. **Vorhersage:** auf 20 neuen Instanzen (Seed + 400 + j) zählt, wie oft der Plan beim geschätzten Gewicht dem Plan beim wahren Gewicht gleicht; der **Regret** der falschen Pläne ist ihr relativer Mehrwert beim wahren Gewicht. **Schätzfehler:** der Entscheider rechnet mit Zahlen, die um eine ganze Zahl von `−a` bis `+a` verschoben sind (mindestens 1); der Beobachter kennt die wahren Zahlen. **Robuste Anpassung:** das Gewicht (ganze Prozent) mit der kleinsten Summe der relativen Regrets der beobachteten Pläne (Gleichstand: das kleinere Gewicht). **Andere Entscheider:** ein ε-Constraint-Entscheider minimiert die Kosten unter einer Zeitgrenze (Anteil des Weges von der besten Zeit zur Zeit des Kosten-Optimums); ein lexikographischer minimiert erst die Kosten, dann die Zeit. **Einheit:** die Zeit mal `f` verschiebt die Haltepunkte von `Δ1 / (Δ1 + Δ2)` auf `Δ1 / (Δ1 + f·Δ2)`. Formeln stehen im 📐-Expander der App.

## Methodik

Die App zeigt: die Intervalle je Entscheidung mit dem Schnitt (Balkendiagramm), die Vorhersage auf neuen Instanzen, die Kurve der Regret-Summe (robuste Anpassung), die Wahl eines ε-Constraint-Entscheiders Instanz für Instanz und die Einheit. Zählungen über feste Instanzen (20 Versuche mit je 20 Instanzen, 8 Personen, alle 40 320 Pläne; neun verborgene Gewichte von 10 bis 90 %; K = 1, 2, 3, 5, 10, 20) liegen hinter Schaltern. Verdikte entstehen live aus der Rechnung, jede Zahl im Text kommt aus dem Ergebnis.

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen stammen aus den Auswertungsfunktionen der App und sind in `tests/test_claims.py` nachgerechnet. „Zählung“ heißt: 20 Versuche (Seeds `100000 + 20 t`) mit je 20 Instanzen, 8 Personen und Aufgaben, neun verborgene Gewichte, also **180 Fälle** je K und 3 600 Vorhersagen; es sind **Zählungen und Spannen über feste Instanzen**, kein Satz und keine Aussage über andere Instanzen. K = 1 / 2 / 3 / 5 / 10 / 20.

| Frage | Befund |
|---|---|
| Breite der erklärenden Menge, exakter Entscheider (Median in Prozentpunkten) | **25,7 / 14,4 / 11,0 / 6,3 / 3,2 / 1,7** |
| dabei: größte Breite | 76,3 / 47,6 / 33,0 / 20,7 / 15,2 / 9,7 |
| dabei: Breite höchstens 5 Prozentpunkte (von 180) | 2 / 14 / 29 / 62 / 128 / 171 |
| dabei: wahres Gewicht in der Menge | **180 von 180** bei jedem K |
| Fehler der Mitte (Median; Maximum, Prozentpunkte) | 5,1 / 3,2 / 2,3 / 1,5 / 0,7 / 0,3; Maximum 31,9 / 16,0 / 16,0 / 9,2 / 6,3 / 3,5 |
| Vorhersage richtig, mit der Mitte (von 3 600) | 2 540 / 2 948 / 3 066 / 3 232 / 3 375 / 3 489 (**70,6 / 81,9 / 85,2 / 89,8 / 93,8 / 96,9 %**) |
| dabei: Regret der falschen Pläne (Median; Maximum) | Median 0 %; Maximum 31,6 / 11,1 / 11,1 / 7,8 / 3,9 / 2,0 % |
| Schätzfehler ±5: eine einzelne Entscheidung durch kein Gewicht erklärbar | **518 von 3 600 (14,4 %)** |
| dabei: erklärende Menge nicht leer (von 180) | 148 / 117 / 92 / 56 / 9 / **0** |
| dabei, wenn nicht leer: Breite (Median) | 27,3 / 14,0 / 9,0 / 6,2 / 1,9 |
| robuste Anpassung: Fehler des Gewichts (Median; Maximum, Prozentpunkte) | **10 / 6 / 4,5 / 3 / 2 / 1**; Maximum 66 / 48 / 23 / 17 / 17 / 9 |
| robuste Anpassung: Vorhersage richtig (von 3 600) | 1 926 / 2 442 / 2 657 / 2 920 / 3 167 / 3 302 (53,5 / 67,8 / 73,8 / 81,1 / 88,0 / 91,7 %) |
| ε-Constraint-Entscheider, Zeitgrenze 20 / 40 / 60 %: durch ein Gewicht erklärbar (von 400) | **209 / 206 / 221** (52,2 / 51,5 / 55,2 %); nur an einem Haltepunkt 0 / 0 / 1; Breite (Median) 17,4 / 16,1 / 16,6 |
| lexikographischer Entscheider: Breite der erklärenden Gewichte (Minimum / Median / Maximum) | 0,7 / 14,4 / 80,6 Prozentpunkte |
| Zeit mal 10 (Gewicht 50 %, 20 Instanzen): das erklärende Intervall ändert sich; dieselben Ecken | **20 von 20**; 20 von 20 |
| Preset „Fünf Entscheidungen lassen ein Intervall offen“ (Seed 100000) | Gewichte **35,8 bis 41,7 %** (Breite 5,9), wahres Gewicht 40 % darin, Mitte 38,8 %; Vorhersage 19 von 20, robuste Anpassung (36 %) 17 von 20; ε-Constraint (40 %) in 10 von 20 erklärbar |
| Preset „Eine Entscheidung lässt viel offen“ (Seed 100060, K = 1) | **57,5 bis 100 %** (Breite 42,5), Mitte 78,8 % (18,8 Prozentpunkte daneben), Vorhersage nur **7 von 20**; die robuste Anpassung (58 %) trifft 19 von 20 |
| Preset „Zwanzig Entscheidungen“ (Seed 100040) | **29,4 bis 30,7 %** (Breite 1,3), wahres Gewicht 30 %, Vorhersage 20 von 20 |
| Preset „Kein Gewicht erklärt alles“ (Seed 100000, ±5, K = 10) | Menge **leer**, 2 der 10 Entscheidungen schon einzeln nicht erklärbar; robuste Anpassung 15 % gegen wahr 20 %, Vorhersage 19 von 20 |
| Preset „Einzeln erklärbar, zusammen nicht“ (Seed 100020, ±5, K = 10) | Menge **leer**, aber jede Entscheidung für sich erklärbar; robuste Anpassung 70 % gleich dem wahren Gewicht, Vorhersage 20 von 20 |
| Preset „Zeitgrenzen-Entscheider: nur ein Teil erklärbar“ (Seed 100020) | der ε-Constraint-Entscheider (Grenze 40 %) ist in **8 von 20** Entscheidungen durch ein Gewicht erklärbar; die Mitte der fünf Entscheidungen des Gewichts-Entscheiders (35,8 %) sagt 13 von 20 voraus |
| Preset „Andere Einheit, anderes Gewicht“ (Seed 100020, Zeit mal 10) | dieselbe Entscheidung erklärt die Gewichte **6,6 bis 100 %** statt 41,6 bis 100 % |
| Preset „Kleinstes Beispiel (3 Personen)“ (Seed 100020) | 6 Pläne, 3 Entscheidungen lassen **42,1 bis 62,6 %** offen, Mitte 52,4 %, Vorhersage 20 von 20; ε-Constraint in 19 von 20 erklärbar |

**Korrektur der Planungshypothese und Abweichungen von der Messreihe:** „Rückwärts gerechnete Gewichte sind nicht eindeutig“ ist bestätigt, aber präzisiert: **ein Gewicht ist ein Intervall, und das Intervall schrumpft mit den Entscheidungen** (25,7 Prozentpunkte bei einer, 1,7 bei zwanzig). Nicht erwartet war, dass die **exakte** Rückrechnung bei Schätzfehlern mit der Zahl der Entscheidungen **versagt** (null von 180 nichtleer bei zwanzig), obwohl die robuste Anpassung dann immer besser wird, und dass **fast die Hälfte der Entscheidungen** eines ε-Constraint-Entscheiders durch kein Gewicht erklärbar ist. Beides zeigt: die Wahl der Modellklasse (Gewichtssumme) bestimmt, was die Rückrechnung findet. Die Zahlen der Demo weichen leicht von der Messreihe der Planung ab (Breite bei K = 2 14,4 statt 14,7, Vorhersage bei K = 20 96,9 statt 97,3 %, Schätzfehler: 148 statt 150 nichtleere Mengen bei K = 1), aus drei Gründen: die Demo zieht die Kosten aus 11 bis 109 (die Messreihe aus 1 bis 99), damit das Rauschen nie an die Untergrenze 1 stößt; bei Gleichstand am Haltepunkt gilt hier der kleinere Plan-Index (die Messreihe nahm einen Bisektionsschnitt); und der verrauschte Entscheider wird hier mit abgeschnittenen Zahlen neu gemessen. Von der Literatur ist nichts gelesen und nichts zitiert (siehe „Ehrliche Grenzen“).

## Ehrliche Grenzen

- **Ein Zufallsmodell:** Kosten und Zeit 11 bis 109, je Zahl unabhängig, gleichverteiltes Rauschen; echte Entscheider handeln nicht so.
- **Nur die Gewichtssumme als Modell:** die Rückrechnung sucht ein einziges Gewicht; eine nichtlineare Nutzenfunktion (Verfahren wie UTA) kommt nicht vor.
- **Der Beobachter kennt die wahren Zahlen:** nur der Entscheider verschätzt sich; sieht auch der Beobachter nur Schätzungen, wird die Menge zusätzlich verzerrt.
- **Entscheidungen auf verschiedenen Instanzen:** nie zwei Entscheidungen auf derselben Instanz; ein Entscheider mit wechselndem Gewicht oder Anreizen (Mechanism Design) gehört nicht zu diesem Stück.
- **Exakt nur bis n = 8:** alle Pläne aufgezählt (40 320); größere Instanzen brauchen einen Löser für die Hülle.
- **Zwei andere Regeln als Beispiele:** der ε-Constraint- und der lexikographische Entscheider zeigen nur, dass die Gewichtssumme nicht jede Regel erklärt; sie sind keine Auswahl typischer Entscheider.
- **Keine Literatur:** inverse Optimierung und Präferenzlernen sind nur als Namen bekannt; Primärtexte sind nicht gelesen, die Demo übernimmt daraus nichts.
- **Kein Satz:** die Zahlen sind Zählungen über feste Instanzen, nicht allgemein.

## Verifikation

Insgesamt 229 Tests (`pytest tests/`), alle grün.

- **Kern:** Handbeispiele (2 Personen, 2 Aufgaben; die Instanzen A und B der Planung mit allen vier Kombinationen, leerer Menge, Mitte 5/12 und robuster Anpassung am Rand): Summen, Ecken, Haltepunkte 1/3, 4/9 und 1/2, Gleichstand, Einheit (Haltepunkt 1/21), ε-Constraint von Hand; das Intervall jedes Punktes aus der Definition (alle Pläne aus `itertools.permutations`, `Fraction`, Kandidaten aus allen Schnittpunkten, an den Enden der Grenzwert), der gewählte Plan gegen die Aufzählung, die ε-Constraint-Wahl und die robuste Anpassung gegen eine Schleife.
- **Eigenschaften:** das wahre Gewicht liegt beim exakten Entscheider immer in der Menge (24 Fälle mal Gewichte 0 bis 100); die Menge schrumpft mit jeder weiteren Entscheidung; der gewählte Plan hat am wahren Gewicht Regret 0; die robuste Anpassung des exakten Entscheiders liegt in der Menge; die Intervalle der Ecken überdecken [0, 1] ohne Lücke; Kosten wachsen und Zeit fällt entlang der Hülle; die Vorhersage mit dem wahren Gewicht ist fehlerfrei; Schätzfehler bleiben in ±a; die Zeitgrenze 0 liefert die beste Zeit und 100 das Kosten-Optimum, und eine lockerere Grenze macht die Kosten nie höher; eine andere Einheit behält die Ecken und verschiebt die Intervalle nach unten.
- **Randfälle:** eine Person, alle Kosten gleich, gleiche Matrizen, Gewichtsenden 0 und 100, K = 1 und 20, n = 3 und 8, stärkster Schätzfehler.
- **Verdikte:** reine Funktionen, jede Verzweigung und jede Zahl im Text an Presetwerten (`tests/test_verdicts.py`).
- **Presets:** Vollständigkeit, Werte innerhalb der Reglergrenzen, Standard-Preset gleich Standardeinstellung, kein anderes Preset gleich den Voreinstellungen, und dass jedes Preset zeigt, was sein Name sagt.
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jeder Regler am Minimum und Maximum), jedes Preset, alle Zählungen, Footer-Test, Layout.
- **Zählungen:** `tests/test_experiments.py` hält alle Zahlen der vier Zählungen fest; `tests/test_claims.py` jede Zahl dieser README.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App |
| `requirements-dev.txt` | Laufzeit plus pytest |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `zll_algorithm.py` | Kern: Aufzählung, Ecken und Haltepunkte, Intervalle, Schnitt, Regret, robuste Anpassung, ε-Constraint-Wahl |
| `zll_constants.py` | Regler-Grenzen, feste Annahmen, Farben, Presets |
| `zll_evaluation.py` | Entscheider, Rückrechnung, Vorhersage, Zählungen, Verdikte |
| `zll_layout.py` | Fester Kopf (Stylesheet) |
| `zll_pdf_export.py` | PDF-Export der Rückrechnung |
| `zll_presets.py` | Permalink (Begrenzen), Presets (Schnellstart in der Seitenleiste), Zufalls-Button |
| `zll_scenario.py` | Instanzen (zwei Matrizen) und Schätzfehler |
| `zll_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `tests/` | Handbeispiele, Orakel, Eigenschaften, Randfälle, Verdikte, Presets, Zählungen, Claims, Layout, AppTest-Smoke-Test, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- **Keine Anreize und kein Mechanism Design:** die Gliederung nennt „Anreize“ im Titel des Stücks; hier geht es nur um die Rückrechnung aus beobachteten Entscheidungen, nicht darum, wie man Entscheider zu wahrheitsgemäßen Entscheidungen bringt.
- **Keine Nutzenfunktionen und kein Präferenzlernen:** nur ein Gewicht, keine Kurven (UTA und Verwandtes sind eine eigene Linie im Mehrkriterien-Ranking).
- **Keine Hold-out-Menge:** kein Parameter der Demo wurde an den Instanzen gewählt.
- **Kein Löser für die Hülle:** alle Pläne sind aufgezählt.
- **Keine Nachbauten der Literatur.**

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly, NumPy und SciPy.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
