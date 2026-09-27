"""SETTING_SPECS-Permalink-Muster, Presets und Zufalls-Seed-Buttons (Standardmuster aus dem Demo-Portfolio)."""

import random
from dataclasses import dataclass
from typing import Callable, Optional

import streamlit as st

import gc_constants as C
import gc_scenario as gs


@dataclass(frozen=True)
class SettingSpec:
    url_param: str
    caster: Callable
    default: object
    lo: Optional[float] = None
    hi: Optional[float] = None


def _int_choice(options):
    def cast(value):
        value = int(value)
        if value not in options:
            raise ValueError(value)
        return value
    return cast


def _float_choice(options):
    def cast(value):
        value = float(value)
        if value not in options:
            raise ValueError(value)
        return value
    return cast


def _choice_from(options):
    def cast(value):
        value = str(value)
        if value not in options:
            raise ValueError(value)
        return value
    return cast


GREEDY_ORDERS = ("ascending", "shuffled", "bad", "good")

SETTING_SPECS = {
    "kind_select": SettingSpec("kind", _choice_from(C.KINDS), "interval"),
    "n_slider": SettingSpec("n", int, C.DEFAULT_N, C.N_MIN, C.N_MAX),
    "p_select": SettingSpec("p", _float_choice(C.P_OPTIONS), C.DEFAULT_P),
    "kcrown_slider": SettingSpec("kcrown", int, 4, gs.CROWN_MIN_K, gs.CROWN_MAX_K),
    "seed_input": SettingSpec("seed", int, C.DEFAULT_SEED, 0, C.SEED_MAX),
    "greedy_order_select": SettingSpec("order", _choice_from(GREEDY_ORDERS), "ascending"),
    "gc_step": SettingSpec("step", _int_choice(tuple(C.STEPS)), 1),
}
PRESET_KEYS = {"kind": "kind_select", "n": "n_slider", "p": "p_select", "kcrown": "kcrown_slider", "seed": "seed_input", "greedy_order": "greedy_order_select", "step": "gc_step",
               "color_k": "color_k"}
STEP_SLIDERS = ("color_k",)
WIDGET_KEYS = {"n_slider": "n_widget", "p_select": "p_widget", "kcrown_slider": "kcrown_widget", "seed_input": "seed_widget"}


def init_session_state_defaults():
    for state_key, spec in SETTING_SPECS.items():
        if state_key not in st.session_state:
            st.session_state[state_key] = spec.default


def bounds(state_key):
    spec = SETTING_SPECS[state_key]
    return spec.lo, spec.hi


def load_permalink_settings():
    if "permalink_loaded" in st.session_state:
        return
    qp = st.query_params
    for state_key, spec in SETTING_SPECS.items():
        if spec.url_param in qp:
            try:
                value = spec.caster(qp[spec.url_param])
                if spec.lo is not None:
                    value = max(spec.lo, value)
                if spec.hi is not None:
                    value = min(spec.hi, value)
                st.session_state[state_key] = value
            except (ValueError, TypeError):
                pass
    st.session_state["permalink_loaded"] = True


def sync_query_params(values):
    """`values`: {state_key: aktueller Wert}."""
    try:
        for state_key, value in values.items():
            st.query_params[SETTING_SPECS[state_key].url_param] = str(value)
    except Exception:
        pass


def store_from_widget(state_key):
    """Callback: übernimmt den Wert eines nur zeitweise sichtbaren Reglers in den dauerhaft gespeicherten Wert."""
    st.session_state[state_key] = st.session_state[WIDGET_KEYS[state_key]]


def push_to_widget(state_key):
    """Ist der Regler gerade sichtbar, muss ein geänderter gespeicherter Wert (Preset, Würfel) auch ihn selbst ändern."""
    widget_key = WIDGET_KEYS[state_key]
    if widget_key in st.session_state:
        st.session_state[widget_key] = st.session_state[state_key]


def apply_preset(name):
    """Setzt die Einstellungen; der Färbe-Schritt-Regler (Schritt 1) wird geleert und nur gesetzt, wenn das Preset einen Wert über 1 verlangt."""
    for key in STEP_SLIDERS:
        st.session_state.pop(key, None)
    for key, state_key in PRESET_KEYS.items():
        if key in C.PRESETS[name] and not (state_key in STEP_SLIDERS and C.PRESETS[name][key] <= 1):
            st.session_state[state_key] = C.PRESETS[name][key]
    for state_key in WIDGET_KEYS:
        push_to_widget(state_key)


def randomize_seed():
    st.session_state["seed_input"] = random.randint(0, C.SEED_MAX)
    push_to_widget("seed_input")
