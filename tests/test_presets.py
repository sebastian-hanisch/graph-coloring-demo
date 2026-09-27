"""Presets: gültige Werte und jede Zahl der Hilfetexte gegen die echten Auswertungsfunktionen."""

import gc_constants as C
import gc_evaluation as ev
from gc_evaluation import Settings
from gc_presets import PRESET_KEYS, SETTING_SPECS


def _settings(name):
    p = C.PRESETS[name]
    return Settings(p["kind"], p.get("n", C.DEFAULT_N), p.get("p", C.DEFAULT_P), p.get("kcrown", 4), p.get("seed", C.DEFAULT_SEED), p.get("greedy_order", "ascending"))


def _has(name, *values):
    for v in values:
        assert v in C.PRESET_HELP[name], (name, v)


def test_every_preset_has_valid_values_and_a_help_text():
    assert list(C.PRESETS) == list(C.PRESET_HELP) and len(C.PRESETS) == 6
    for name, p in C.PRESETS.items():
        assert set(p) <= set(PRESET_KEYS) and {"kind", "step"} <= set(p) and p["step"] in C.STEPS
        for key, state_key in PRESET_KEYS.items():
            if key in p and state_key in SETTING_SPECS:
                spec = SETTING_SPECS[state_key]
                assert spec.caster(p[key]) == p[key], (name, key)
                if spec.lo is not None:
                    assert spec.lo <= p[key] <= spec.hi, (name, key)
        assert C.PRESET_HELP[name].strip()


def test_help_crown_and_interval_presets():
    a = ev.analyse(_settings("Kronengraph (Lehrbuch)"))
    assert (a.n, a.chi) == (8, 2) and a.greedy.k == 4
    _has("Kronengraph (Lehrbuch)", "8 Knoten (k=4)", "chi = 2", "4 Farben")

    a = ev.analyse(_settings("Intervallgraph (Standardfall)"))
    assert (a.n, a.m, a.omega, a.chi) == (16, 40, 6, 6)
    _has("Intervallgraph (Standardfall)", "16 Lieferzeitfenster", "40 Überlappungen", "omega = chi = 6")

    a = ev.analyse(_settings("Intervallgraph dicht"))
    assert (a.n, a.m, a.omega, a.chi) == (30, 138, 11, 11)
    _has("Intervallgraph dicht", "30 Lieferzeitfenster", "138 Überlappungen", "omega = chi = 11")


def test_help_random_presets():
    settings = _settings("Zufallsgraph: Reihenfolge entscheidet")
    a = ev.analyse(settings)
    assert (a.n, a.chi) == (20, 5)
    ks = ev.order_spread(settings.kind, settings.n, settings.p, settings.k_crown, settings.seed, n_orders=200)
    assert min(ks) == 5 and max(ks) == 7
    _has("Zufallsgraph: Reihenfolge entscheidet", "20 Knoten", "chi = 5", "zwischen 5 und 7")

    a = ev.analyse(_settings("Zufallsgraph dicht (DSATUR-Lücke)"))
    assert (a.n, a.m, a.chi, a.dsatur.k, a.welsh_powell.k, a.greedy.k) == (30, 248, 8, 9, 10, 10)
    _has("Zufallsgraph dicht (DSATUR-Lücke)", "30 Knoten, 248 Kanten", "chi = 8", "DSATUR braucht 9")


def test_help_cost_and_cover_sweep_preset():
    rows_cost = ev.cost_sweep(C.COST_NS)
    assert rows_cost[0]["steps"] == 31 and rows_cost[-1]["steps"] == 6133
    rows_cover = ev.clique_cover_vs_chromatic(C.COST_NS[:5])
    last = rows_cover[-1]
    assert last["n"] == 30 and last["cover"] == 10 and last["chi"] == 5
    _has("Aufwand und Cliquenüberdeckung", "6133 Elementarschritte", "31 bei n=10", "10 Cliquen", "chi(G) = 5")
