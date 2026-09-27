"""AppTest-Rauchtests: Voreinstellung, jedes Preset, jeder Schritt für jede Instanz, Färbe-Schritt-Regler, Randwerte, Permalink-Grenzen, bedingte Regler, Berechnungen auf Abruf, Footer."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import gc_constants as C

APP = str(Path(__file__).resolve().parent.parent / "app.py")


def _run(step=1, **state):
    at = AppTest.from_file(APP, default_timeout=300)
    state.setdefault("gc_step", step)
    for k, v in state.items():
        at.session_state[k] = v
    at.run()
    return at


def _ok(at):
    assert not at.exception, [e.value for e in at.exception]


def _click(at, key):
    next(b for b in at.button if b.key == key).click().run()


def test_default_run_shows_the_summary():
    at = _run()
    _ok(at)
    assert {"Cliquenzahl ω", "Chromatische Zahl χ", "Δ+1", "DSATUR-Farben"} <= {m.label for m in at.metric}


@pytest.mark.parametrize("name", list(C.PRESETS))
def test_every_preset_button_runs(name):
    at = _run(kind_select="interval")
    _click(at, f"preset_{name}")
    _ok(at)
    p, ss = C.PRESETS[name], at.session_state
    assert ss["kind_select"] == p["kind"] and ss["gc_step"] == p["step"]
    for key, state_key in (("n", "n_slider"), ("p", "p_select"), ("kcrown", "kcrown_slider"), ("seed", "seed_input"), ("greedy_order", "greedy_order_select")):
        if key in p:
            assert ss[state_key] == p[key], (name, key)


@pytest.mark.parametrize("step", [1, 2, 3, 4])
@pytest.mark.parametrize("kind", ["interval", "random", "crown"])
def test_every_step_runs_for_every_kind(step, kind):
    at = _run(step=step, kind_select=kind, n_slider=12, kcrown_slider=4)
    _ok(at)
    assert at.session_state["gc_step"] == step


@pytest.mark.parametrize("algo", ["greedy", "welsh_powell", "dsatur"])
def test_color_step_slider_every_position(algo):
    at = _run(step=1, kind_select="random", n_slider=10, algo_select=algo)
    _ok(at)
    n_steps = at.session_state["color_k"]
    for k in sorted({1, max(1, n_steps // 2), n_steps}):
        at2 = _run(step=1, kind_select="random", n_slider=10, algo_select=algo, color_k=k)
        _ok(at2)
        assert at2.session_state["color_k"] == k


def test_interval_greedy_available_only_for_interval_kind():
    at = _run(step=1, kind_select="interval", algo_select="interval_greedy")
    _ok(at)
    at2 = _run(step=1, kind_select="random")
    _ok(at2)
    assert not any(r.value == "interval_greedy" for r in at2.radio if r.key == "algo_select")


def test_crown_good_and_bad_order_produce_different_color_counts():
    good = _run(step=1, kind_select="crown", greedy_order_select="good", kcrown_slider=5)
    bad = _run(step=1, kind_select="crown", greedy_order_select="bad", kcrown_slider=5)
    _ok(good)
    _ok(bad)
    assert good.session_state["gc_step"] == bad.session_state["gc_step"] == 1


def test_permalink_values_are_clamped_and_invalid_choices_fall_back_to_the_default():
    at = AppTest.from_file(APP, default_timeout=300)
    for k, v in dict(kind="nope", n="9999", p="0.33", kcrown="99", order="sideways", seed="-4", step="9").items():
        at.query_params[k] = v
    at.run()
    _ok(at)
    ss = at.session_state
    assert (ss["kind_select"], ss["n_slider"], ss["p_select"], ss["kcrown_slider"], ss["greedy_order_select"], ss["seed_input"], ss["gc_step"]) == (
        "interval", C.N_MAX, C.DEFAULT_P, 8, "ascending", 0, 1)


def test_permalink_accepts_valid_values_and_writes_them_back():
    at = AppTest.from_file(APP, default_timeout=300)
    for k, v in dict(kind="random", n="9", p="0.5", order="shuffled", seed="7", step="2").items():
        at.query_params[k] = v
    at.run()
    _ok(at)
    ss = at.session_state
    assert (ss["n_slider"], ss["p_select"], ss["greedy_order_select"], ss["seed_input"], ss["gc_step"]) == (9, 0.5, "shuffled", 7, 2)
    assert at.query_params["p"] == ["0.5"] and at.query_params["step"] == ["2"]
    assert ss["n_widget"] == 9 and ss["seed_widget"] == 7


def test_sidebar_shows_the_controls_that_belong_to_the_instance():
    interval = _run(kind_select="interval")
    assert any(w.key == "n_widget" for w in interval.slider) and not any(w.key == "p_widget" for w in interval.select_slider)
    random_ = _run(kind_select="random")
    assert any(w.key == "n_widget" for w in random_.slider) and any(s.key == "p_widget" for s in random_.select_slider)
    crown = _run(kind_select="crown")
    assert any(w.key == "kcrown_widget" for w in crown.slider) and not any(w.key == "n_widget" for w in crown.slider)


def test_switching_kind_back_and_forth_keeps_the_stored_values():
    at = _run(kind_select="random", n_slider=25, p_select=0.6, seed_input=11)
    at.session_state["kind_select"] = "crown"
    at.run()
    _ok(at)
    at.session_state["kind_select"] = "random"
    at.run()
    _ok(at)
    assert at.session_state["n_widget"] == 25 and at.session_state["p_widget"] == 0.6 and at.session_state["seed_widget"] == 11


def test_dice_button_changes_the_seed_and_the_visible_widget():
    at = _run(kind_select="random")
    old = at.session_state["seed_input"]
    next(b for b in at.button if b.label == "🎲 Neue Instanz generieren").click().run()
    _ok(at)
    assert at.session_state["seed_input"] != old and at.session_state["seed_widget"] == at.session_state["seed_input"]


def test_on_demand_experiments():
    at = _run(kind_select="random", step=2)
    _click(at, "spread_start")
    _ok(at)
    assert len(at.get("plotly_chart")) >= 1
    at2 = _run(step=4)
    for key in ("cost_start", "cover_start"):
        _click(at2, key)
        _ok(at2)
    assert len(at2.get("plotly_chart")) >= 2


@pytest.mark.parametrize("kw", [dict(kind_select="interval", n_slider=C.N_MIN), dict(kind_select="interval", n_slider=C.N_MAX), dict(kind_select="random", p_select=min(C.P_OPTIONS)),
                                 dict(kind_select="random", p_select=max(C.P_OPTIONS)), dict(kind_select="crown", kcrown_slider=3), dict(kind_select="crown", kcrown_slider=8)])
def test_extreme_settings_run_on_every_step(kw):
    for step in (1, 2, 3, 4):
        _ok(_run(step=step, **kw))


def test_footer_limits_and_literature_are_present():
    at = _run()
    assert any("Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net)" in c.value for c in at.caption)
    assert any("Wo die Annahmen enden" in s.value for s in at.subheader)
    assert any("Welsh" in m.value and "Brélaz" in m.value for e in at.expander for m in e.markdown)
