"""Auswertung: Settings/analyse-Konsistenz, Sweeps."""

import gc_algorithm as ga
import gc_constants as C
import gc_evaluation as ev
import gc_scenario as gs
from gc_evaluation import Settings


def test_analyse_matches_direct_computation_for_each_kind():
    for settings in (Settings("interval", 14, seed=7), Settings("random", 14, 0.4, seed=7), Settings("crown", k_crown=4, greedy_order="good")):
        a = ev.analyse(settings)
        if settings.kind == "interval":
            inst = gs.interval_instance(settings.n, seed=settings.seed)
        elif settings.kind == "random":
            inst = gs.random_conflict_instance(settings.n, settings.p, settings.seed)
        else:
            inst, _, _ = gs.crown_instance(settings.k_crown)
        adj = ga.adjacency(inst.n, inst.edges)
        assert a.n == inst.n and a.m == inst.m
        assert a.delta == ga.max_degree(adj)
        assert ga.is_proper_coloring(adj, a.greedy.colors)
        assert ga.is_proper_coloring(adj, a.welsh_powell.colors)
        assert ga.is_proper_coloring(adj, a.dsatur.colors)


def test_crown_greedy_order_setting_selects_the_right_permutation():
    good = ev.analyse(Settings("crown", k_crown=5, greedy_order="good"))
    bad = ev.analyse(Settings("crown", k_crown=5, greedy_order="bad"))
    assert good.greedy.k == 2 and bad.greedy.k == 5


def test_order_spread_only_for_interval_and_random():
    ks = ev.order_spread("random", 14, 0.4, 4, seed=1, n_orders=30)
    assert len(ks) == 30 and all(isinstance(k, int) for k in ks)
    import pytest
    with pytest.raises(ValueError):
        ev.order_spread("crown", 14, 0.4, 4, seed=1)


def test_gap_sweep_ratios_are_at_least_one():
    rows = ev.gap_sweep("random", (10, 15))
    for r in rows:
        assert r["greedy"] >= 1.0 and r["welsh_powell"] >= 1.0 and r["dsatur"] >= 1.0


def test_bound_sweep_orders_hold():
    rows = ev.bound_sweep("random", (10, 15, 20))
    for r in rows:
        assert r["omega"] <= r["chi"] <= r["delta_plus_1"]


def test_interval_optimality_check_is_always_one():
    assert ev.interval_optimality_check([8, 12, 16]) == 1.0


def test_bipartite_dsatur_check_is_always_one():
    assert ev.bipartite_dsatur_check([(4, 4), (6, 6)]) == 1.0


def test_cost_sweep_length_and_positive_steps():
    rows = ev.cost_sweep((10, 15))
    assert len(rows) == 2
    assert all(r["steps"] > 0 for r in rows)


def test_clique_cover_vs_chromatic_cover_at_least_chi():
    rows = ev.clique_cover_vs_chromatic((10, 15))
    for r in rows:
        if r["chi"]:
            assert r["cover"] >= r["chi"]
