"""Auswertung: Färbungen, Schranken, Reihenfolge-Streuung, Aufwand der exakten Suche, Cliquenüberdeckung."""

from dataclasses import dataclass

import gc_algorithm as ga
import gc_constants as C
import gc_scenario as gs


@dataclass
class Settings:
    kind: str = "interval"          # "interval" | "random" | "crown"
    n: int = C.DEFAULT_N
    p: float = C.DEFAULT_P
    k_crown: int = 4
    seed: int = C.DEFAULT_SEED
    greedy_order: str = "ascending"  # "ascending" | "shuffled" (interval/random) | "bad" | "good" (crown)


@dataclass
class Analysis:
    n: int
    m: int
    delta: int
    omega: int
    chi: int                        # None, wenn exact_limit überschritten
    greedy: object
    welsh_powell: object
    dsatur: object
    interval_greedy: object = None  # nur kind == "interval"


def _instance(settings):
    if settings.kind == "interval":
        return gs.interval_instance(settings.n, seed=settings.seed)
    if settings.kind == "random":
        return gs.random_conflict_instance(settings.n, settings.p, settings.seed)
    if settings.kind == "crown":
        inst, bad, good = gs.crown_instance(settings.k_crown)
        return inst
    raise ValueError(f"unbekannte Instanzart {settings.kind}")


def _greedy_order(settings, inst):
    if settings.kind == "crown":
        _, bad, good = gs.crown_instance(settings.k_crown)
        return bad if settings.greedy_order == "bad" else good
    order = list(range(inst.n))
    if settings.greedy_order == "shuffled":
        import random
        random.Random(int(settings.seed) * 1_000_003 + 8123).shuffle(order)
    return order


def analyse(settings, exact_limit=C.EXACT_LIMIT):
    inst = _instance(settings)
    adj = ga.adjacency(inst.n, inst.edges)
    order = _greedy_order(settings, inst)
    greedy = ga.greedy_color(adj, order)
    wp = ga.welsh_powell(adj)
    ds = ga.dsatur(adj)
    omega, _ = ga.clique_number(adj, exact_limit)
    chi, _ = ga.chromatic_number(adj, exact_limit)
    ig = ga.interval_greedy(inst, adj) if settings.kind == "interval" else None
    return Analysis(inst.n, inst.m, ga.max_degree(adj), omega, chi, greedy, wp, ds, ig)


def order_spread(kind, n, p, k_crown, seed, n_orders=200):
    """Greedy über `n_orders` zufällige Reihenfolgen auf DERSELBEN Instanz (kind in interval/random); gibt die Liste der benutzten Farbenzahlen zurück."""
    import random
    if kind == "crown":
        raise ValueError("order_spread gilt nur für interval/random - der Kronengraph hat die feste gute/schlechte Reihenfolge")
    inst = gs.interval_instance(n, seed=seed) if kind == "interval" else gs.random_conflict_instance(n, p, seed)
    adj = ga.adjacency(inst.n, inst.edges)
    rng = random.Random(int(seed) * 1_000_003 + 9911)
    ks = []
    order = list(range(inst.n))
    for _ in range(n_orders):
        rng.shuffle(order)
        ks.append(ga.greedy_color(adj, order).k)
    return ks


def _median(vals):
    vals = sorted(vals)
    mid = len(vals) // 2
    return vals[mid] if len(vals) % 2 else (vals[mid - 1] + vals[mid]) / 2


def gap_sweep(kind, ns, p=C.DEFAULT_P, seeds=C.SWEEP_SEEDS, exact_limit=C.EXACT_LIMIT):
    """Median-Verhältnis Greedy(aufsteigend)/Welsh-Powell/DSATUR gegen chi über die Größe, je Instanzart."""
    out = []
    for n in ns:
        greedy_ratios, wp_ratios, ds_ratios = [], [], []
        for seed in seeds:
            s = Settings(kind, n, p, seed=seed)
            a = analyse(s, exact_limit)
            if a.chi:
                greedy_ratios.append(a.greedy.k / a.chi)
                wp_ratios.append(a.welsh_powell.k / a.chi)
                ds_ratios.append(a.dsatur.k / a.chi)
        out.append({"n": n, "greedy": _median(greedy_ratios), "welsh_powell": _median(wp_ratios), "dsatur": _median(ds_ratios)})
    return out


def bound_sweep(kind, ns, p=C.DEFAULT_P, seeds=C.SWEEP_SEEDS, exact_limit=C.EXACT_LIMIT):
    """Median von omega, chi und Delta+1 über die Größe."""
    out = []
    for n in ns:
        omegas, chis, bounds = [], [], []
        for seed in seeds:
            s = Settings(kind, n, p, seed=seed)
            a = analyse(s, exact_limit)
            if a.chi:
                omegas.append(a.omega)
                chis.append(a.chi)
                bounds.append(a.delta + 1)
        out.append({"n": n, "omega": _median(omegas), "chi": _median(chis), "delta_plus_1": _median(bounds)})
    return out


def cost_sweep(ns, p=C.DEFAULT_P, seeds=C.SWEEP_SEEDS, exact_limit=60):
    """Elementarschritte der exakten chi-Suche über die Größe (Median über `seeds`, Zufallsgraph)."""
    out = []
    for n in ns:
        steps = []
        chis = []
        for seed in seeds:
            inst = gs.random_conflict_instance(n, p, seed)
            adj = ga.adjacency(inst.n, inst.edges)
            chi, s = ga.chromatic_number(adj, exact_limit)
            steps.append(s)
            chis.append(chi)
        out.append({"n": n, "steps": _median(steps), "chi": _median(chis)})
    return out


def interval_optimality_check(ns, seeds=C.SWEEP_SEEDS, exact_limit=C.EXACT_LIMIT):
    """Anteil der Intervallgraph-Instanzen, bei denen Greedy nach Startzeit exakt chi trifft (sollte immer 100 % sein - Satz)."""
    total = matched = 0
    for n in ns:
        for seed in seeds:
            inst = gs.interval_instance(n, seed=seed)
            adj = ga.adjacency(inst.n, inst.edges)
            chi, _ = ga.chromatic_number(adj, exact_limit)
            if chi is None:
                continue
            ig = ga.interval_greedy(inst, adj)
            total += 1
            matched += int(ig.k == chi)
    return matched / total if total else None


def bipartite_dsatur_check(pairs, p=0.4, seeds=C.SWEEP_SEEDS):
    """Anteil der Zufalls-Bipartitgraphen, bei denen DSATUR <= 2 Farben benutzt (sollte immer 100 % sein - Spezialfall-Satz)."""
    total = matched = 0
    for n_a, n_b in pairs:
        for seed in seeds:
            inst = gs.random_bipartite_instance(n_a, n_b, p, seed)
            adj = ga.adjacency(inst.n, inst.edges)
            total += 1
            matched += int(ga.dsatur(adj).k <= 2)
    return matched / total if total else None


def clique_cover_vs_chromatic(ns, p=C.DEFAULT_P, seeds=C.SWEEP_SEEDS, exact_limit=C.EXACT_LIMIT):
    """Median der Cliquenüberdeckungszahl (DSATUR auf dem Komplement) gegen chi(G) selbst - zwei verschiedene Fragen am selben Graphen."""
    out = []
    for n in ns:
        covers, chis = [], []
        for seed in seeds:
            inst = gs.random_conflict_instance(n, p, seed)
            adj = ga.adjacency(inst.n, inst.edges)
            classes, _ = ga.clique_cover_dsatur(adj)
            chi, _ = ga.chromatic_number(adj, exact_limit)
            covers.append(len(classes))
            if chi:
                chis.append(chi)
        out.append({"n": n, "cover": _median(covers), "chi": _median(chis) if chis else None})
    return out
