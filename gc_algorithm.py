"""Knotenfärbung: Greedy (reihenfolgeabhängig), Welsh-Powell (Grad absteigend), DSATUR (Sättigungsgrad, dynamisch), exakte chromatische Zahl (Backtracking mit Cliquenzahl als Schranke).

**Elementarschritte** (das Aufwandsmaß dieser Reihe, keine Laufzeit): jeder gefärbte/besuchte Knoten und jede von einem Ende angesehene Kante zählt 1, wie in den Geschwister-Demos; die exakte Suche zählt
zusätzlich jeden Backtracking-Knoten (Versuch, eine Farbe zu vergeben) als einen Schritt.

Begriffe: eine **Färbung** weist jedem Knoten eine Farbe zu, sodass keine zwei benachbarten Knoten dieselbe Farbe haben. Die **chromatische Zahl** chi(G) ist die kleinste Farbenzahl, mit der das gelingt.
Klassische Schranken: omega(G) <= chi(G) <= Delta(G) + 1 (Cliquenzahl, Maximalgrad)."""

import random
from dataclasses import dataclass, field


def adjacency(n, edges, order="fixed", seed=0):
    """Adjazenzliste aus ungerichteten Kanten (u, v); "fixed" = aufsteigende Nachbarn, "shuffled" = je Knoten gemischt (Seed fest, Python-`random`)."""
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    for lst in adj:
        lst.sort()
    if order == "shuffled":
        rng = random.Random(int(seed) * 1_000_003 + 5150)
        for lst in adj:
            rng.shuffle(lst)
    elif order != "fixed":
        raise ValueError(f"unbekannte Reihenfolge {order}")
    return adj


def degrees(adj):
    return [len(lst) for lst in adj]


def max_degree(adj):
    return max(degrees(adj), default=0)


# --- Greedy, Welsh-Powell, DSATUR -----------------------------------------------------------------------------------------------------------------


@dataclass
class ColoringResult:
    colors: list                                   # Farbe je Knoten (0, 1, ...)
    k: int                                          # Zahl der benutzten Farben
    steps: int
    events: list = field(default_factory=list)     # ("color", Knoten, Farbe) in Vergabereihenfolge
    method: str = ""


def _smallest_free_color(used):
    c = 0
    while c in used:
        c += 1
    return c


def greedy_color(adj, order, method="greedy"):
    """Je Knoten in `order` die kleinste Farbe, die kein bereits gefärbter Nachbar schon hat. Reihenfolgeabhängig: dieselbe Instanz kann mit verschiedenen Reihenfolgen sehr unterschiedlich viele Farben
    brauchen (bis zu Delta(G) + 1 im schlechtesten Fall - siehe Kronengraph)."""
    n = len(adj)
    colors = [-1] * n
    steps = 0
    events = []
    for v in order:
        steps += 1
        used = set()
        for u in adj[v]:
            steps += 1
            if colors[u] != -1:
                used.add(colors[u])
        c = _smallest_free_color(used)
        colors[v] = c
        events.append(("color", v, c))
    k = (max(colors) + 1) if colors else 0
    return ColoringResult(colors, k, steps, events, method)


def welsh_powell(adj):
    """Greedy in absteigender Gradreihenfolge (Gleichstand: kleinster Index) - Welsh und Powell 1967."""
    order = sorted(range(len(adj)), key=lambda v: (-len(adj[v]), v))
    return greedy_color(adj, order, "welsh_powell")


def dsatur(adj):
    """Brélaz 1979: wiederholt der ungefärbte Knoten mit größtem **Sättigungsgrad** (Zahl verschiedener Farben unter bereits gefärbten Nachbarn) gewählt, bei Gleichstand größter Grad im Gesamtgraphen (nicht Brélaz' Restgrad der ungefärbten Nachbarn - wie networkx), dann
    kleinster Index; erhält die kleinste freie Farbe. Anders als Greedy/Welsh-Powell ist die Reihenfolge nicht vorab fest, sondern entsteht während der Färbung."""
    n = len(adj)
    colors = [-1] * n
    sat_colors = [set() for _ in range(n)]
    deg = degrees(adj)
    remaining = set(range(n))
    steps = 0
    events = []
    for _ in range(n):
        v = max(remaining, key=lambda x: (len(sat_colors[x]), deg[x], -x))
        steps += 1
        c = _smallest_free_color(sat_colors[v])
        colors[v] = c
        events.append(("color", v, c))
        remaining.discard(v)
        for u in adj[v]:
            steps += 1
            if colors[u] == -1:
                sat_colors[u].add(c)
    k = (max(colors) + 1) if colors else 0
    return ColoringResult(colors, k, steps, events, "dsatur")


def interval_greedy(inst, adj):
    """Greedy in nach Startzeit sortierter Reihenfolge (Gleichstand: kleinster Index) - auf Intervallgraphen (perfekte Graphen) beweisbar optimal: chi == omega."""
    order = sorted(range(inst.n), key=lambda v: (inst.intervals[v][0], v))
    return greedy_color(adj, order, "interval_greedy")


def is_proper_coloring(adj, colors):
    return all(colors[u] != colors[v] for u in range(len(adj)) for v in adj[u])


# --- Cliquenzahl (Branch-and-Bound) ----------------------------------------------------------------------------------------------------------------


def clique_number(adj, exact_limit=None):
    """Größte Clique per Branch-and-Bound (Einschließen/Ausschließen je Kandidat, Schranke Größe + Restkandidaten <= bisher bestes). Gibt (omega, steps) zurück, oder (None, 0), wenn `exact_limit`
    überschritten ist."""
    n = len(adj)
    if exact_limit is not None and n > exact_limit:
        return None, 0
    if n == 0:
        return 0, 0
    adjset = [set(a) for a in adj]
    best = [0]
    steps = [0]

    def expand(candidates, size):
        steps[0] += 1
        if not candidates:
            if size > best[0]:
                best[0] = size
            return
        if size + len(candidates) <= best[0]:
            return
        v = next(iter(candidates))
        rest = candidates - {v}
        expand(candidates & adjset[v], size + 1)
        if size + len(rest) > best[0]:
            expand(rest, size)

    expand(set(range(n)), 0)
    return best[0], steps[0]


# --- Chromatische Zahl (Backtracking, Cliquenzahl als untere Schranke) -----------------------------------------------------------------------------


def chromatic_number(adj, exact_limit=None):
    """Für k = omega(G), omega(G)+1, ... wird per Backtracking eine gültige k-Färbung gesucht (Farbsymmetrie-Abbruch: eine neue Farbe wird nur probiert, wenn sie höchstens die bisher größte benutzte + 1
    ist); das erste erfolgreiche k ist chi(G). Gibt (chi, steps) zurück, oder (None, 0), wenn `exact_limit` überschritten ist."""
    n = len(adj)
    if exact_limit is not None and n > exact_limit:
        return None, 0
    if n == 0:
        return 0, 0
    omega, omega_steps = clique_number(adj, exact_limit)
    order = sorted(range(n), key=lambda v: -len(adj[v]))
    total_steps = [omega_steps]

    def try_k(k):
        colors = [-1] * n

        def backtrack(i, max_used):
            total_steps[0] += 1
            if i == n:
                return True
            v = order[i]
            forbidden = {colors[u] for u in adj[v] if colors[u] != -1}
            hi = min(max_used + 1, k - 1)
            for c in range(hi + 1):
                if c in forbidden:
                    continue
                colors[v] = c
                if backtrack(i + 1, max(max_used, c)):
                    return True
                colors[v] = -1
            return False

        return backtrack(0, -1)

    k = max(omega, 1)
    while not try_k(k):
        k += 1
    return k, total_steps[0]


# --- Cliquenüberdeckung (Färbung des Komplementgraphen) -------------------------------------------------------------------------------------------


def complement(adj):
    """Der Komplementgraph: u und v sind benachbart genau dann, wenn sie es in `adj` NICHT sind."""
    n = len(adj)
    adjset = [set(a) for a in adj]
    return [[u for u in range(n) if u != v and u not in adjset[v]] for v in range(n)]


def color_classes(colors):
    classes = {}
    for v, c in enumerate(colors):
        classes.setdefault(c, []).append(v)
    return [sorted(vs) for vs in classes.values()]


def is_clique(adj, nodes):
    adjset = [set(a) for a in adj]
    return all(v in adjset[u] for i, u in enumerate(nodes) for v in nodes[i + 1:])


def clique_cover_dsatur(adj):
    """Cliquenüberdeckung über DSATUR auf dem Komplementgraphen: jede Farbklasse der Komplement-Färbung ist eine Clique im Original."""
    comp = complement(adj)
    result = dsatur(comp)
    return color_classes(result.colors), result
