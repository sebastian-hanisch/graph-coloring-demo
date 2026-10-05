"""Unabhängiges Orakel: chromatische Zahl gegen CP-SAT (n bis 20), Cliquenzahl gegen networkx, Greedy/Welsh-Powell/DSATUR gegen eine eigene Neuimplementierung mit denselben Gleichstandsregeln
(DSATUR: Sättigung, dann Grad im Gesamtgraphen, dann kleinster Index), Intervallgraphen: Greedy nach Startzeit == Maximum gleichzeitig offener Fenster == chi."""

import random

import pytest

import gc_algorithm as ga
import gc_scenario as gs

nx = pytest.importorskip("networkx")
cp_model = pytest.importorskip("ortools.sat.python.cp_model")


def _chi_cp(n, edges):
    if not edges:
        return 1 if n else 0
    m = cp_model.CpModel()
    x = [[m.NewBoolVar("") for _ in range(n)] for _ in range(n)]
    used = [m.NewBoolVar("") for _ in range(n)]
    for v in range(n):
        m.AddExactlyOne(x[v])
        for c in range(n):
            m.AddImplication(x[v][c], used[c])
    for a, b in edges:
        for c in range(n):
            m.AddBoolOr([x[a][c].Not(), x[b][c].Not()])
    m.Minimize(sum(used))
    s = cp_model.CpSolver()
    s.parameters.num_workers = 1
    s.parameters.max_time_in_seconds = 20
    assert s.Solve(m) == cp_model.OPTIMAL
    return int(s.ObjectiveValue())


def _greedy_ref(n, edges, order):
    nb = {v: set() for v in range(n)}
    for u, v in edges:
        nb[u].add(v)
        nb[v].add(u)
    col = {}
    for v in order:
        c = 0
        while any(col.get(u) == c for u in nb[v]):
            c += 1
        col[v] = c
    return [col[v] for v in range(n)], nb


def _dsatur_ref(n, edges):
    nb = {v: set() for v in range(n)}
    for u, v in edges:
        nb[u].add(v)
        nb[v].add(u)
    col = {}
    while len(col) < n:
        v = max((x for x in range(n) if x not in col), key=lambda x: (len({col[u] for u in nb[x] if u in col}), len(nb[x]), -x))
        c = 0
        while any(col.get(u) == c for u in nb[v]):
            c += 1
        col[v] = c
    return [col[v] for v in range(n)]


def test_random_graphs_against_cpsat_networkx_and_reference_heuristics():
    rng = random.Random(8)
    for it in range(120):
        n = rng.randrange(1, 17)
        p = rng.choice([0.1, 0.3, 0.5, 0.8])
        edges = sorted((u, v) for u in range(n) for v in range(u + 1, n) if rng.random() < p)
        adj = ga.adjacency(n, edges, "shuffled" if it % 2 else "fixed", seed=it)
        g = nx.Graph()
        g.add_nodes_from(range(n))
        g.add_edges_from(edges)
        chi = ga.chromatic_number(adj)[0]
        assert chi == _chi_cp(n, edges), (n, edges)
        assert ga.clique_number(adj)[0] == max(len(c) for c in nx.find_cliques(g))
        order = list(range(n))
        rng.shuffle(order)
        assert ga.greedy_color(adj, order).colors == _greedy_ref(n, edges, order)[0]
        assert ga.welsh_powell(adj).colors == _greedy_ref(n, edges, sorted(range(n), key=lambda v: (-len(adj[v]), v)))[0]
        ds = ga.dsatur(adj)
        assert ds.colors == _dsatur_ref(n, edges) and chi <= ds.k <= ga.max_degree(adj) + 1


def test_interval_graphs_greedy_by_start_equals_max_overlap_equals_chi():
    for n in range(4, 20):
        for seed in range(5):
            inst = gs.interval_instance(n, seed=400000 + seed)
            adj = ga.adjacency(inst.n, inst.edges)
            overlap = max(sum(1 for a, b in inst.intervals if a <= s < b) for s, _ in inst.intervals)
            assert ga.interval_greedy(inst, adj).k == overlap == ga.chromatic_number(adj)[0]
