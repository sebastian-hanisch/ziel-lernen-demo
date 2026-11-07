"""Konstanten: Regler-Grenzen, feste Annahmen, Farben und Presets."""

N_MIN, N_MAX, DEFAULT_N = 3, 8, 8             # Zuordnung n mal n; alle n! Pläne werden aufgezählt (bis 8! = 40 320)
SEED_MAX, DEFAULT_SEED = 999999, 100000       # die Entscheidung j eines Versuchs steht auf der Instanz mit dem Seed (Seed + j)
COST_LOW, COST_HIGH = 11, 109                 # Kosten und Zeit: ganze Zahlen (Versatz 10: das Rauschen bis 10 stößt nie an die Untergrenze 1)

W_MIN, W_MAX, W_STEP, DEFAULT_W = 0, 100, 1, 40         # verborgenes Gewicht der Zeit in Prozent: Ziel (100 - w) * Kosten + w * Zeit
K_MIN, K_MAX, DEFAULT_K = 1, 20, 5                      # Zahl der beobachteten Entscheidungen
A_MIN, A_MAX, A_STEP, DEFAULT_A = 0, 10, 1, 0           # Schätzfehler des Entscheiders: jede Zahl der Matrizen um -a bis +a (0: er rechnet exakt)
FRAC_MIN, FRAC_MAX, FRAC_STEP, DEFAULT_FRAC = 0, 100, 10, 40   # ε-Constraint: Zeitgrenze in Prozent des Weges von der besten Zeit zur Zeit des Kosten-Optimums
UNITS = (1, 2, 5, 10)                                   # Faktor auf die Zeit (andere Einheit)
DEFAULT_UNIT = 0
TEST_OFFSET = 400                                       # die Test-Instanzen (Vorhersage) stehen bei Seed + 400 + j
N_TEST = 20
GRID = tuple(range(0, 101))                             # Raster der robusten Anpassung: ganze Prozent

SWEEP_TRIALS = 20                                       # Versuche; Versuch t beginnt bei Seed 100000 + 20 t
SWEEP_PER_TRIAL = 20                                    # Instanzen je Versuch
SWEEP_BASE = 100000
SWEEP_WS = tuple(range(10, 100, 10))                    # verborgene Gewichte in Prozent
SWEEP_KS = (1, 2, 3, 5, 10, 20)
SWEEP_N = 8
SWEEP_A = 5                                             # Schätzfehler der verrauschten Zählung
SWEEP_FRACS = (20, 40, 60)

COLOR_BAR = "#4c78a8"
COLOR_BAD = "#c0504d"
COLOR_SET = "#2F6B65"
COLOR_TRUE = "#d8a13a"
COLOR_FIT = "#7b5ea7"

PRESETS = {
    "Fünf Entscheidungen lassen ein Intervall offen": {"n": 8, "seed": 100000, "w": 40, "k": 5, "a": 0, "frac": 40, "unit": 0},
    "Eine Entscheidung lässt viel offen": {"n": 8, "seed": 100060, "w": 60, "k": 1, "a": 0, "frac": 40, "unit": 0},
    "Zwanzig Entscheidungen": {"n": 8, "seed": 100040, "w": 30, "k": 20, "a": 0, "frac": 40, "unit": 0},
    "Kein Gewicht erklärt alles": {"n": 8, "seed": 100000, "w": 20, "k": 10, "a": 5, "frac": 40, "unit": 0},
    "Einzeln erklärbar, zusammen nicht": {"n": 8, "seed": 100020, "w": 70, "k": 10, "a": 5, "frac": 40, "unit": 0},
    "Zeitgrenzen-Entscheider: nur ein Teil erklärbar": {"n": 8, "seed": 100020, "w": 40, "k": 5, "a": 0, "frac": 40, "unit": 0},
    "Andere Einheit, anderes Gewicht": {"n": 8, "seed": 100020, "w": 50, "k": 5, "a": 0, "frac": 40, "unit": 3},
    "Kleinstes Beispiel (3 Personen)": {"n": 3, "seed": 100020, "w": 50, "k": 3, "a": 0, "frac": 40, "unit": 0},
}

PRESET_HELP = {
    "Fünf Entscheidungen lassen ein Intervall offen": "Fünf Entscheidungen eines Entscheiders mit Zeitgewicht 40 %: erklärt werden die Gewichte von 35,8 bis 41,7 % (Breite 5,9 Prozentpunkte), die Mitte sagt 19 von 20 neue Pläne richtig voraus.",
    "Eine Entscheidung lässt viel offen": "Nach einer einzigen Entscheidung bleiben die Gewichte von 57,5 bis 100 % offen; die Mitte (78,8 %) liegt 18,8 Prozentpunkte vom wahren Gewicht 60 % und sagt nur 7 von 20 Pläne richtig voraus.",
    "Zwanzig Entscheidungen": "Mit 20 Entscheidungen schrumpft die erklärende Menge auf die Gewichte von 29,4 bis 30,7 % (1,3 Prozentpunkte); die Vorhersage trifft 20 von 20.",
    "Kein Gewicht erklärt alles": "Der Entscheider schätzt die Zahlen mit Fehler bis 5: kein Gewicht erklärt alle 10 Entscheidungen, 2 davon schon einzeln nicht. Die robuste Anpassung findet 15 % statt 20 %.",
    "Einzeln erklärbar, zusammen nicht": "Jede der 10 Entscheidungen ist für sich durch ein Gewicht erklärbar, alle zusammen nicht (Schätzfehler bis 5). Die robuste Anpassung trifft das wahre Gewicht 70 % genau.",
    "Zeitgrenzen-Entscheider: nur ein Teil erklärbar": "Ein Entscheider, der die Kosten unter einer Zeitgrenze (40 % des Weges) minimiert, ist auf 20 Instanzen nur in 8 Entscheidungen durch ein Gewicht erklärbar.",
    "Andere Einheit, anderes Gewicht": "Dieselbe Entscheidung, die Zeit mal 10 gerechnet: erklärt werden die Gewichte von 6,6 bis 100 % statt 41,6 bis 100 %. Das Gewicht gilt nur in den Einheiten der Rechnung.",
    "Kleinstes Beispiel (3 Personen)": "Drei Personen, drei Aufgaben (6 Pläne): drei Entscheidungen lassen die Gewichte von 42,1 bis 62,6 % offen; der Zeitgrenzen-Entscheider ist in 19 von 20 Entscheidungen erklärbar.",
}
