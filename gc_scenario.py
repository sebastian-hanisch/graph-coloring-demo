"""Die Instanzen dieser Demo: ein **Intervallgraph** (Lieferzeitfenster an einem Verteilzentrum - zwei Lieferungen kollidieren, wenn sich ihre Zeitfenster überlappen; ein perfekter Graph, chi = omega),
ein **Zufalls-Konfliktgraph** G(n,p) ohne Intervallstruktur, und das Lehrbuchbeispiel **Kronengraph** (bipartit, chi = 2, aber in schlechter Reihenfolge zwingt Greedy bis zu Delta+1 Farben).

Knoten sind von 0 bis n - 1 durchnummeriert; Kanten sind Paare (u, v) mit u < v, sortiert."""

import random
from dataclasses import dataclass, field

import gc_constants as C


@dataclass(frozen=True)
class Instance:
    edges: tuple                        # ((u, v), ...) sortiert, u < v
    n: int
    kind: str = "interval"
    intervals: tuple = field(default=())    # nur Intervallgraph: ((start, ende), ...) je Knoten
    seed: int = 0
    labels: tuple = field(default=())       # Knotennamen (nur Lehrbuchbeispiel)

    @property
    def m(self):
        return len(self.edges)


def make_rng(seed, salt):
    """Zufallsquelle mit fester, plattformunabhängiger Zahlenfolge (Python-`random`)."""
    return random.Random(int(seed) * 1_000_003 + int(salt))


# --- Intervallgraph: Lieferzeitfenster --------------------------------------------------------------------------------------------------------------


def interval_instance(n=C.DEFAULT_N, span=C.DEFAULT_SPAN, min_len=C.DEFAULT_MIN_LEN, max_len=C.DEFAULT_MAX_LEN, seed=C.DEFAULT_SEED):
    """`n` Zeitfenster [start, start+laenge) auf einer Achse der Länge `span`; zwei Fenster sind benachbart, wenn sie sich überlappen. Ein Intervallgraph ist immer ein perfekter Graph (chi = omega)."""
    n = int(n)
    if n < 1:
        raise ValueError("mindestens 1 Knoten")
    rng = make_rng(seed, 3301)
    intervals = []
    for _ in range(n):
        length = rng.uniform(min_len, max_len)
        start = rng.uniform(0, max(span - length, 0.001))
        intervals.append((start, start + length))
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            a0, a1 = intervals[i]
            b0, b1 = intervals[j]
            if a0 < b1 and b0 < a1:
                edges.append((i, j))
    return Instance(tuple(sorted(edges)), n, "interval", tuple(intervals), int(seed))


# --- Zufalls-Konfliktgraph ---------------------------------------------------------------------------------------------------------------------------


def random_conflict_instance(n=C.DEFAULT_N, p=C.DEFAULT_P, seed=C.DEFAULT_SEED):
    """G(n, p): jedes der n*(n-1)/2 Kandidatenpaare wird unabhängig mit Wahrscheinlichkeit p zu einer Konfliktkante."""
    n = int(n)
    if n < 1:
        raise ValueError("mindestens 1 Knoten")
    if not 0.0 <= p <= 1.0:
        raise ValueError("p muss in [0, 1] liegen")
    rng = make_rng(seed, 7717)
    edges = [(i, j) for i in range(n) for j in range(i + 1, n) if rng.random() < p]
    return Instance(tuple(edges), n, "random", (), int(seed))


# --- Handgebautes Lehrbuchbeispiel: Kronengraph -------------------------------------------------------------------------------------------------------

CROWN_MIN_K, CROWN_MAX_K = 3, 8


def crown_instance(k=4):
    """Der **Kronengraph** S_k^0: 2k Knoten {a_0..a_{k-1}, b_0..b_{k-1}}, Kante a_i - b_j fuer jedes i != j (aber NIE a_i - b_i). Bipartit, chi = 2 (Seite a / Seite b); jeder Knoten hat Grad k - 1, also
    Delta + 1 = k. Knoten a_i hat Index i, Knoten b_i hat Index k + i. `bad_order`: a_0, b_0, a_1, b_1, ... - jeder neu hinzukommende Knoten trifft auf alle bisherigen der anderen Seite ausser seinem
    "Partner", der noch nicht gefaerbt ist - Greedy vergibt in dieser Reihenfolge k verschiedene Farben. `good_order`: erst alle a, dann alle b - Greedy findet die optimalen 2 Farben."""
    k = int(k)
    if not CROWN_MIN_K <= k <= CROWN_MAX_K:
        raise ValueError(f"k muss zwischen {CROWN_MIN_K} und {CROWN_MAX_K} liegen")
    edges = [(i, k + j) for i in range(k) for j in range(k) if i != j]
    labels = tuple([f"a{i}" for i in range(k)] + [f"b{i}" for i in range(k)])
    bad_order = [x for i in range(k) for x in (i, k + i)]
    good_order = list(range(k)) + [k + i for i in range(k)]
    inst = Instance(tuple(sorted(edges)), 2 * k, "crown", (), 0, labels)
    return inst, bad_order, good_order


# --- Zufalls-Bipartitgraph (fuer den DSATUR-Spezialfall-Test) -----------------------------------------------------------------------------------------


def random_bipartite_instance(n_a, n_b, p, seed):
    """Zufalls-Bipartitgraph: Seite A (Knoten 0..n_a-1) und Seite B (Knoten n_a..n_a+n_b-1), jede Kante zwischen den Seiten unabhaengig mit Wahrscheinlichkeit p."""
    rng = make_rng(seed, 5551)
    edges = [(i, n_a + j) for i in range(n_a) for j in range(n_b) if rng.random() < p]
    return Instance(tuple(sorted(edges)), n_a + n_b, "bipartite", (), int(seed))
