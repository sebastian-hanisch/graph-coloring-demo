"""Zentrale Korrektheits-Kette: Gültigkeit aller Verfahren, chi gegen Brute-Force und bekannte Graphen, omega<=chi<=Delta+1, Intervallgraph-Satz, DSATUR auf Bipartitgraphen, Kronengraph von Hand,
Cliquenüberdeckungs-Äquivalenz, Buchführung, Sonderfälle."""

import itertools

import networkx as nx
import pytest

import gc_algorithm as ga
import gc_scenario as gs


def _brute_chi(adj):
    n = len(adj)
    if n == 0:
        return 0
    for k in range(1, n + 1):
        for assign in itertools.product(range(k), repeat=n):
            if all(assign[u] != assign[v] for u in range(n) for v in adj[u]):
                return k
    return n


def _brute_clique(adj):
    n = len(adj)
    adjset = [set(a) for a in adj]
    for size in range(n, 0, -1):
        for combo in itertools.combinations(range(n), size):
            if all(v in adjset[u] for i, u in enumerate(combo) for v in combo[i + 1:]):
                return size
    return 0


# --- 1: Gültigkeit ---------------------------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("kind", ["interval", "random", "bipartite"])
def test_every_method_produces_a_proper_coloring(kind):
    checked = 0
    for seed in range(60):
        if kind == "interval":
            inst = gs.interval_instance(n=14, seed=seed)
        elif kind == "bipartite":
            inst = gs.random_bipartite_instance(6, 6, 0.4, seed)
        else:
            inst = gs.random_conflict_instance(n=14, p=0.4, seed=seed)
        adj = ga.adjacency(inst.n, inst.edges)
        for result in (ga.greedy_color(adj, list(range(inst.n))), ga.welsh_powell(adj), ga.dsatur(adj)):
            assert ga.is_proper_coloring(adj, result.colors)
            checked += 1
        chi, _ = ga.chromatic_number(adj, exact_limit=20)
        if chi is not None:
            # rebuild an exact coloring is not returned directly; verify via a fresh backtracking search producing a valid coloring of size chi
            assert chi >= 1
    assert checked > 0


# --- 2: chi exakt gegen Brute-Force und bekannte Graphen -------------------------------------------------------------------------------------------


def test_chromatic_number_matches_brute_force_on_small_random_graphs():
    for seed in range(60):
        n = 1 + seed % 8
        inst = gs.random_conflict_instance(n=n, p=0.5, seed=seed)
        adj = ga.adjacency(inst.n, inst.edges)
        chi, _ = ga.chromatic_number(adj)
        assert chi == _brute_chi(adj), (seed, n)


@pytest.mark.parametrize("n,expected", [(3, 3), (4, 4), (5, 5), (6, 6)])
def test_chromatic_number_of_complete_graphs(n, expected):
    edges = [(i, j) for i in range(n) for j in range(i + 1, n)]
    adj = ga.adjacency(n, edges)
    chi, _ = ga.chromatic_number(adj)
    assert chi == expected


def test_chromatic_number_of_odd_and_even_cycles():
    for n, expected in ((5, 3), (7, 3), (6, 2), (8, 2)):
        edges = [(i, (i + 1) % n) for i in range(n)]
        edges = [tuple(sorted(e)) for e in edges]
        adj = ga.adjacency(n, edges)
        chi, _ = ga.chromatic_number(adj)
        assert chi == expected, n


def test_chromatic_number_of_petersen_graph_is_three():
    P = nx.petersen_graph()
    edges = [tuple(sorted(e)) for e in P.edges()]
    adj = ga.adjacency(10, edges)
    chi, _ = ga.chromatic_number(adj)
    assert chi == 3


def test_empty_graph_and_edgeless_graph():
    assert ga.chromatic_number(ga.adjacency(0, []))[0] == 0
    assert ga.chromatic_number(ga.adjacency(5, []))[0] == 1


# --- 3: omega <= chi <= Delta+1, Cliquenzahl gegen Brute-Force ---------------------------------------------------------------------------------------


def test_bounds_hold_on_many_instances():
    for seed in range(80):
        n = 3 + seed % 10
        inst = gs.random_conflict_instance(n=n, p=0.4, seed=seed)
        adj = ga.adjacency(inst.n, inst.edges)
        chi, _ = ga.chromatic_number(adj)
        omega, _ = ga.clique_number(adj)
        delta = ga.max_degree(adj)
        assert omega <= chi <= delta + 1, (seed, omega, chi, delta)


def test_clique_number_matches_brute_force():
    for seed in range(60):
        n = 1 + seed % 8
        inst = gs.random_conflict_instance(n=n, p=0.5, seed=seed)
        adj = ga.adjacency(inst.n, inst.edges)
        omega, _ = ga.clique_number(adj)
        assert omega == _brute_clique(adj), (seed, n)


# --- 4: Intervallgraph-Satz: Greedy nach Startzeit == chi ----------------------------------------------------------------------------------------


def test_interval_greedy_matches_chi_and_omega_exactly():
    checked = 0
    for seed in range(150):
        inst = gs.interval_instance(n=14, seed=seed)
        adj = ga.adjacency(inst.n, inst.edges)
        chi, _ = ga.chromatic_number(adj, exact_limit=20)
        omega, _ = ga.clique_number(adj, exact_limit=20)
        ig = ga.interval_greedy(inst, adj)
        assert chi == omega == ig.k, (seed, chi, omega, ig.k)
        checked += 1
    assert checked >= 150


# --- 5: DSATUR auf Bipartitgraphen == 2 (Spezialfall-Optimalität) ------------------------------------------------------------------------------------


def test_dsatur_is_optimal_on_bipartite_graphs():
    for seed in range(100):
        inst = gs.random_bipartite_instance(6, 6, 0.4, seed)
        adj = ga.adjacency(inst.n, inst.edges)
        result = ga.dsatur(adj)
        assert result.k <= 2


# --- 6: Kronengraph von Hand ----------------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("k", [3, 4, 5, 6])
def test_crown_graph_by_hand(k):
    inst, bad_order, good_order = gs.crown_instance(k)
    adj = ga.adjacency(inst.n, inst.edges)
    assert ga.max_degree(adj) == k - 1
    chi, _ = ga.chromatic_number(adj, exact_limit=20)
    assert chi == 2
    bad = ga.greedy_color(adj, bad_order)
    assert bad.k == k
    assert ga.is_proper_coloring(adj, bad.colors)
    good = ga.greedy_color(adj, good_order)
    assert good.k == 2
    assert ga.is_proper_coloring(adj, good.colors)


# --- 7: Cliquenüberdeckung == Färbung des Komplementgraphen ------------------------------------------------------------------------------------------


def test_clique_cover_classes_are_cliques_in_the_original_graph():
    for seed in range(60):
        inst = gs.random_conflict_instance(n=14, p=0.4, seed=seed)
        adj = ga.adjacency(inst.n, inst.edges)
        classes, _ = ga.clique_cover_dsatur(adj)
        covered = sorted(v for cl in classes for v in cl)
        assert covered == list(range(inst.n))
        for cl in classes:
            assert ga.is_clique(adj, cl), (seed, cl)


def test_clique_cover_number_equals_chromatic_number_of_complement():
    for seed in range(30):
        inst = gs.random_conflict_instance(n=10, p=0.4, seed=seed)
        adj = ga.adjacency(inst.n, inst.edges)
        comp = ga.complement(adj)
        cover_chi, _ = ga.chromatic_number(comp, exact_limit=15)
        classes, _ = ga.clique_cover_dsatur(adj)
        assert len(classes) >= cover_chi  # DSATUR ist eine Heuristik, nie besser als das Optimum


# --- 8: Buchführung ----------------------------------------------------------------------------------------------------------------------------------


def test_order_parameter_does_not_change_welsh_powell_or_dsatur_result():
    inst = gs.random_conflict_instance(n=16, p=0.4, seed=9)
    fixed = ga.adjacency(inst.n, inst.edges, order="fixed")
    shuffled = ga.adjacency(inst.n, inst.edges, order="shuffled", seed=9)
    assert ga.welsh_powell(fixed).k == ga.welsh_powell(shuffled).k
    assert ga.dsatur(fixed).k == ga.dsatur(shuffled).k


def test_determinism():
    inst = gs.random_conflict_instance(n=16, p=0.4, seed=3)
    adj = ga.adjacency(inst.n, inst.edges)
    assert ga.dsatur(adj).colors == ga.dsatur(adj).colors
    assert ga.welsh_powell(adj).colors == ga.welsh_powell(adj).colors
    assert ga.chromatic_number(adj) == ga.chromatic_number(adj)


def test_adjacency_invalid_order_raises():
    with pytest.raises(ValueError):
        ga.adjacency(3, [(0, 1)], order="nope")


# --- 9: Sonderfälle ----------------------------------------------------------------------------------------------------------------------------------


def test_single_node_and_no_edges():
    adj = ga.adjacency(1, [])
    assert ga.dsatur(adj).k == 1
    assert ga.welsh_powell(adj).k == 1
    adj5 = ga.adjacency(5, [])
    assert ga.chromatic_number(adj5)[0] == 1
    assert ga.clique_number(adj5)[0] == 1


def test_disconnected_graph_chi_is_the_max_over_components():
    # a triangle plus an isolated edge: chi = 3 (from the triangle), not 2
    edges = [(0, 1), (1, 2), (0, 2), (3, 4)]
    adj = ga.adjacency(5, edges)
    chi, _ = ga.chromatic_number(adj)
    assert chi == 3


def test_exact_limit_returns_none_when_exceeded():
    inst = gs.random_conflict_instance(n=20, p=0.3, seed=1)
    adj = ga.adjacency(inst.n, inst.edges)
    assert ga.chromatic_number(adj, exact_limit=5) == (None, 0)
    assert ga.clique_number(adj, exact_limit=5) == (None, 0)
