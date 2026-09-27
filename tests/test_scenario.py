"""Instanzen: Intervallgraph (Zeitfenster), Zufalls-Konfliktgraph, Kronengraph, Zufalls-Bipartitgraph."""

import pytest

import gc_algorithm as ga
import gc_scenario as gs


def test_interval_instance_edges_match_overlap():
    inst = gs.interval_instance(n=12, seed=3)
    for i in range(inst.n):
        for j in range(i + 1, inst.n):
            a0, a1 = inst.intervals[i]
            b0, b1 = inst.intervals[j]
            overlap = a0 < b1 and b0 < a1
            assert overlap == ((i, j) in inst.edges), (i, j, overlap)


def test_random_conflict_instance_matches_the_requested_probability_roughly():
    inst = gs.random_conflict_instance(n=200, p=0.3, seed=1)
    max_m = 200 * 199 // 2
    assert 0.2 * max_m < inst.m < 0.4 * max_m


def test_crown_instance_structure():
    inst, bad, good = gs.crown_instance(4)
    assert inst.n == 8 and inst.m == 4 * 3
    adj = ga.adjacency(inst.n, inst.edges)
    assert all(len(a) == 3 for a in adj)
    assert sorted(bad) == sorted(good) == list(range(8))
    assert (0, 4) not in inst.edges and (0, 5) in inst.edges


def test_crown_instance_range_errors():
    with pytest.raises(ValueError):
        gs.crown_instance(2)
    with pytest.raises(ValueError):
        gs.crown_instance(9)


def test_random_bipartite_instance_has_only_cross_edges():
    inst = gs.random_bipartite_instance(5, 6, 0.5, seed=2)
    for u, v in inst.edges:
        assert (u < 5) != (v < 5)


def test_determinism_and_platform_independent_stream():
    for kind_call in (
        lambda: gs.interval_instance(n=12, seed=7),
        lambda: gs.random_conflict_instance(n=12, p=0.4, seed=7),
        lambda: gs.random_bipartite_instance(5, 5, 0.4, seed=7),
    ):
        a, b = kind_call(), kind_call()
        assert a.edges == b.edges


def test_errors():
    with pytest.raises(ValueError):
        gs.interval_instance(n=0)
    with pytest.raises(ValueError):
        gs.random_conflict_instance(n=0)
    with pytest.raises(ValueError):
        gs.random_conflict_instance(n=5, p=1.5)
