"""Regler-Grenzen, feste Annahmen, gemessene Werte und Presets."""

SEED_MAX = 999999
DEFAULT_SEED = 35

N_MIN, N_MAX, DEFAULT_N = 4, 35, 16
DEFAULT_SPAN = 20.0
DEFAULT_MIN_LEN, DEFAULT_MAX_LEN = 1.0, 5.0
P_OPTIONS = (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9)
DEFAULT_P = 0.3

KINDS = ("interval", "random", "crown")
KIND_LABELS = {"interval": "Intervallgraph (Lieferzeitfenster)", "random": "Zufallsgraph (allgemeine Konflikte)", "crown": "Lehrbuchbeispiel: Kronengraph"}
ORDERS = ("fixed", "shuffled")
ORDER_LABELS = {"fixed": "feste Reihenfolge (nach Knotennummer)", "shuffled": "gemischt (nach Seed)"}
ALGOS = ("greedy", "welsh_powell", "dsatur")
ALGO_LABELS = {"greedy": "Greedy (gegebene Reihenfolge)", "welsh_powell": "Welsh-Powell (Grad absteigend)", "dsatur": "DSATUR (Sättigungsgrad)"}
STEPS = {1: "1 · Greedy in Aktion", 2: "2 · Reihenfolge entscheidet", 3: "3 · Wer kommt am nächsten an χ?", 4: "4 · Aufwand und Cliquenüberdeckung"}

EXACT_LIMIT = 35
SWEEP_SEEDS = tuple(range(100000, 100005))
COST_NS = (10, 15, 20, 25, 30, 35, 40)

# --- Gemessene Werte (2026-09-27, alle Werte über ev.* nachgerechnet, s. tests/test_claims.py) ---
# LÜCKE GEGEN CHI (Zufallsgraph, Median über 5 feste Instanzen Seeds 100000-100004, p=0.3): Greedy(aufsteigend)/Welsh-Powell/DSATUR gegen chi = 1.0/1.0/1.0 (n=10) bis 1.4/1.2/1.0 (n=30) - DSATUR
#   trifft chi in dieser Stichprobe immer exakt, Greedy und Welsh-Powell nicht. Bei p=0.5 (dichter) verfehlt DSATUR chi gelegentlich (Median-Verhältnis 1.125 bei n=30) - kein Beweis der Optimalität.
# SCHRANKEN (Zufallsgraph p=0.3): omega/chi/Delta+1 = 3/3/5 (n=10), 4/4/9 (n=15), 3/4/10 (n=20), 5/5/14 (n=25), 5/5/15 (n=30) - Delta+1 ist meist deutlich lockerer als omega.
# INTERVALLGRAPH-SATZ: Greedy nach Startzeit == chi auf 100 % von >= 500 gemessenen Intervallgraph-Instanzen (n=8..25, Seeds 100000-100004) - der Beweis, nicht nur eine Beobachtung.
# DSATUR AUF BIPARTITGRAPHEN: <= 2 Farben auf 100 % von 20 gemessenen Zufalls-Bipartitgraphen (n_a,n_b = 4..10, Seeds 100000-100004).
# AUFWAND (exakte Suche, Zufallsgraph p=0.3, Median über 5 Seeds): 31/52/129/117/464/3961/6133 Elementarschritte bei n=10/15/20/25/30/35/40.
# CLIQUENÜBERDECKUNG gegen chi(G) (Zufallsgraph p=0.3, Median): 5/3 (n=10), 7/4 (n=15), 9/4 (n=20), 9/5 (n=25), 10/5 (n=30).

PRESETS = {
    "Kronengraph (Lehrbuch)": {"kind": "crown", "kcrown": 4, "greedy_order": "bad", "step": 1},
    "Intervallgraph (Standardfall)": {"kind": "interval", "n": 16, "seed": 35, "greedy_order": "ascending", "step": 3},
    "Intervallgraph dicht": {"kind": "interval", "n": 30, "seed": 35, "greedy_order": "ascending", "step": 3},
    "Zufallsgraph: Reihenfolge entscheidet": {"kind": "random", "n": 20, "p": 0.4, "seed": 35, "greedy_order": "shuffled", "step": 2},
    "Zufallsgraph dicht (DSATUR-Lücke)": {"kind": "random", "n": 30, "p": 0.5, "seed": 100001, "greedy_order": "ascending", "step": 3},
    "Aufwand und Cliquenüberdeckung": {"kind": "random", "n": 35, "p": 0.3, "seed": 35, "greedy_order": "ascending", "step": 4},
}
PRESET_HELP = {
    "Kronengraph (Lehrbuch)": "8 Knoten (k=4), bipartit: chi = 2. Die schlechte Reihenfolge (a₀,b₀,a₁,b₁,...) zwingt Greedy zu 4 Farben (= Δ+1) - obwohl 2 reichen würden.",
    "Intervallgraph (Standardfall)": "16 Lieferzeitfenster, 40 Überlappungen: omega = chi = 6 - Greedy nach Startzeit trifft die chromatische Zahl exakt, wie immer bei Intervallgraphen.",
    "Intervallgraph dicht": "30 Lieferzeitfenster, 138 Überlappungen: omega = chi = 11 - auch bei viel mehr Überlappungen bleibt Greedy nach Startzeit exakt.",
    "Zufallsgraph: Reihenfolge entscheidet": "20 Knoten, chi = 5: über 200 zufällige Reihenfolgen braucht Greedy zwischen 5 und 7 Farben - derselbe Graph, dieselbe Regel, unterschiedliches Ergebnis.",
    "Zufallsgraph dicht (DSATUR-Lücke)": "30 Knoten, 248 Kanten: chi = 8, aber DSATUR braucht 9 Farben (Welsh-Powell und Greedy sogar 10) - DSATUR ist eine sehr gute Heuristik, kein Beweis.",
    "Aufwand und Cliquenüberdeckung": "Über die Größe gemessen: die exakte Suche braucht bei n=40 im Median 6133 Elementarschritte (31 bei n=10); die Cliquenüberdeckung braucht bei n=30 im Median 10 Cliquen "
                                     "gegen chi(G) = 5 - zwei verschiedene Fragen am selben Graphen.",
}
