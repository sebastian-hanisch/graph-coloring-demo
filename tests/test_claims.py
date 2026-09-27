"""Jede Zahl aus README und Konstanten-Kommentar, nachgerechnet über die echten Auswertungsfunktionen."""

from functools import lru_cache

import gc_constants as C
import gc_evaluation as ev


@lru_cache(maxsize=None)
def _gap():
    return {r["n"]: r for r in ev.gap_sweep("random", (10, 15, 20, 25, 30))}


@lru_cache(maxsize=None)
def _bounds():
    return {r["n"]: r for r in ev.bound_sweep("random", (10, 15, 20, 25, 30))}


@lru_cache(maxsize=None)
def _cost():
    return {r["n"]: r for r in ev.cost_sweep(C.COST_NS)}


@lru_cache(maxsize=None)
def _cover():
    return {r["n"]: r for r in ev.clique_cover_vs_chromatic(C.COST_NS[:5])}


def test_gap_sweep_values():
    g = _gap()
    assert [g[n]["greedy"] for n in (10, 15, 20, 25, 30)] == [1.0, 1.2, 1.25, 1.25, 1.4]
    assert [g[n]["welsh_powell"] for n in (10, 15, 20, 25, 30)] == [1.0, 1.0, 1.0, 1.2, 1.2]
    assert [g[n]["dsatur"] for n in (10, 15, 20, 25, 30)] == [1.0, 1.0, 1.0, 1.0, 1.0]


def test_dsatur_gap_appears_at_higher_density():
    rows = {r["n"]: r for r in ev.gap_sweep("random", (30,), p=0.5)}
    assert rows[30]["dsatur"] == 1.125


def test_bound_sweep_values():
    b = _bounds()
    assert [(b[n]["omega"], b[n]["chi"], b[n]["delta_plus_1"]) for n in (10, 15, 20, 25, 30)] == [(3, 3, 5), (4, 4, 9), (3, 4, 10), (5, 5, 14), (5, 5, 15)]


def test_interval_theorem_over_many_instances():
    assert ev.interval_optimality_check((8, 12, 16, 20, 25)) == 1.0


def test_bipartite_dsatur_over_many_instances():
    assert ev.bipartite_dsatur_check([(4, 4), (6, 6), (8, 8), (10, 10)]) == 1.0


def test_cost_sweep_values():
    c = _cost()
    assert [c[n]["steps"] for n in C.COST_NS] == [31, 52, 129, 117, 464, 3961, 6133]


def test_cover_vs_chi_values():
    cov = _cover()
    assert [(cov[n]["cover"], cov[n]["chi"]) for n in (10, 15, 20, 25, 30)] == [(5, 3), (7, 4), (9, 4), (9, 5), (10, 5)]
