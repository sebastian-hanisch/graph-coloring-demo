"""Graphfärbung: Greedy, Welsh-Powell, DSATUR, exakt - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Fünftes Stück der Graphen-und-Netzwerke-Reihe der "Konzepte"-Reihe. Kind der Wurzel (BFS und DFS): eine Knotenfärbung weist jedem Knoten eine Farbe zu, sodass keine zwei benachbarten Knoten dieselbe
Farbe haben; die chromatische Zahl ist reihenfolgeabhängig für Greedy, aber bei Intervallgraphen beweisbar optimal.

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import gc_algorithm as ga
import gc_constants as C
import gc_evaluation as ev
import gc_scenario as gs
from gc_evaluation import Settings, analyse
from gc_presets import apply_preset, bounds, init_session_state_defaults, load_permalink_settings, randomize_seed, store_from_widget, sync_query_params
from gc_visualization import build_cost_sweep, build_cover_vs_chi, build_good_vs_bad, build_methods_vs_bounds, build_network, build_order_histogram, build_timeline

st.set_page_config(page_title="Graphfärbung – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return analyse(settings)


@st.cache_data(show_spinner=False)
def _order_spread(kind, n, p, k_crown, seed):
    return ev.order_spread(kind, n, p, k_crown, seed)


@st.cache_data(show_spinner=False)
def _cost_sweep():
    return ev.cost_sweep(C.COST_NS)


@st.cache_data(show_spinner=False)
def _cover_sweep():
    return ev.clique_cover_vs_chromatic(C.COST_NS[:5])


def _german(x):
    return f"{x:,}".replace(",", ".") if isinstance(x, int) else x


def _colors_at_step(result, k):
    colors = [-1] * len(result.colors)
    for _, v, c in result.events[:k]:
        colors[v] = c
    return colors


st.title("🎨 Graphfärbung – Greedy, Welsh-Powell, DSATUR, exakt")
st.markdown(
    """
**Fünftes Stück der Graphen-und-Netzwerke-Reihe.** Eine **Knotenfärbung** weist jedem Knoten eine Farbe zu, sodass keine zwei benachbarten Knoten dieselbe Farbe haben; die **chromatische Zahl** χ(G)
ist die kleinste Farbenzahl, mit der das gelingt. Klassische Schranken: **ω(G) ≤ χ(G) ≤ Δ(G) + 1** (Cliquenzahl, Maximalgrad). **Greedy** (feste Reihenfolge, kleinste freie Farbe je Knoten) ist
*reihenfolgeabhängig*: dieselbe Instanz kann mit verschiedenen Reihenfolgen sehr unterschiedlich viele Farben brauchen. **Welsh-Powell** (1967, Grad absteigend) und **DSATUR** (Brélaz 1979,
Sättigungsgrad) sind zwei feste Strategien dagegen; eine **exakte** Suche (Backtracking mit der Cliquenzahl als untere Schranke) findet χ selbst für kleine Graphen. Bei **Intervallgraphen** ist Greedy
nach Startzeit sortiert beweisbar optimal (χ = ω); beim **Kronengraphen** zeigt eine schlechte Reihenfolge das Gegenteil.
"""
)
st.caption(
    "Kind der BFS-und-DFS-Demo (fünftes Stück der Graphen-und-Netzwerke-Reihe); Nachfolger (inzwischen gebaut): Zentralität, Strukturkennzahlen, Robustheit, Kaskaden, kritische Knoten härten, "
    "Bandbreite. Eine **Cliquenüberdeckung** (kleinste Zahl von Cliquen, die alle Knoten überdecken) ist genau die Färbung des Komplementgraphen - die Brücke zu Stück 12 (Bandbreite von G(n,k,b))."
)

with st.expander("So funktionieren die vier Verfahren", expanded=True):
    st.markdown(
        """
1. **Greedy:** je Knoten in einer gegebenen Reihenfolge die kleinste Farbe, die kein bereits gefärbter Nachbar schon hat. Einfach, aber reihenfolgeabhängig - im schlechtesten Fall braucht es Δ+1 Farben,
   selbst wenn χ viel kleiner ist (siehe Kronengraph).
2. **Welsh-Powell:** Greedy in absteigender Gradreihenfolge - Knoten mit vielen Nachbarn zuerst, damit sie noch die freie Wahl haben.
3. **DSATUR:** wählt dynamisch den Knoten mit dem größten **Sättigungsgrad** (Zahl verschiedener Farben unter bereits gefärbten Nachbarn) - reagiert auf den tatsächlichen Verlauf der Färbung, nicht nur
   auf den ursprünglichen Grad.
4. **Exakt:** Backtracking-Suche mit Farbsymmetrie-Abbruch, beginnend bei der Cliquenzahl ω(G) als untere Schranke - findet χ(G) selbst, aber nur für kleine Graphen praktikabel.
        """
    )

if C.PRESETS:
    st.caption("🎯 Schnellstart – ein Beispielszenario laden:")
    preset_names = list(C.PRESETS.keys())
    for row in (preset_names[:4], preset_names[4:]):
        if not row:
            continue
        cols = st.columns(len(row))
        for col, name in zip(cols, row):
            with col:
                st.button(name, width="stretch", on_click=apply_preset, args=(name,), help=C.PRESET_HELP.get(name, ""), key=f"preset_{name}")

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()
ss = st.session_state

with st.sidebar:
    st.header("⚙️ Einstellungen")
    kind = st.radio("Instanz", options=list(C.KINDS), format_func=lambda v: C.KIND_LABELS[v], key="kind_select",
                     help="Intervallgraph: Lieferzeitfenster, die sich überlappen (immer ein perfekter Graph, χ = ω). Zufallsgraph: beliebige Konflikte. Kronengraph: bipartit (χ=2), zeigt die "
                     "Reihenfolgeabhängigkeit von Greedy im Extrem.")
    n, p, k_crown = C.DEFAULT_N, C.DEFAULT_P, 4
    if kind in ("interval", "random"):
        n = st.slider("Knotenzahl", *bounds("n_slider"), value=int(ss["n_slider"]), key="n_widget", on_change=store_from_widget, args=("n_slider",))
        if kind == "random":
            p = st.select_slider("Kantenwahrscheinlichkeit", options=list(C.P_OPTIONS), value=float(ss["p_select"]), format_func=lambda v: f"{v * 100:.0f} %", key="p_widget",
                                  on_change=store_from_widget, args=("p_select",))
        seed = st.number_input("Zufalls-Seed der Instanz", *bounds("seed_input"), value=int(ss["seed_input"]), key="seed_widget", step=1, on_change=store_from_widget, args=("seed_input",))
        st.button("🎲 Neue Instanz generieren", width="stretch", on_click=randomize_seed)
    else:
        k_crown = st.slider("Knoten je Seite (k)", *bounds("kcrown_slider"), value=int(ss["kcrown_slider"]), key="kcrown_widget", on_change=store_from_widget, args=("kcrown_slider",),
                             help="Der Kronengraph hat 2k Knoten; Δ = k-1.")
        seed = int(ss["seed_input"])
    if kind == "crown":
        greedy_order = st.radio("Reihenfolge für Greedy", options=["good", "bad"], format_func=lambda v: "gute Reihenfolge (erst alle a, dann alle b)" if v == "good" else "schlechte Reihenfolge "
                                 "(abwechselnd a, b)", key="greedy_order_select")
    else:
        greedy_order = st.radio("Reihenfolge für Greedy", options=["ascending", "shuffled"], format_func=lambda v: "aufsteigende Knotennummer" if v == "ascending" else "zufällig gemischt (Seed)",
                                 key="greedy_order_select")

sync_query_params({"kind_select": kind, "n_slider": int(n) if kind in ("interval", "random") else int(ss["n_slider"]), "p_select": float(p) if kind == "random" else float(ss["p_select"]),
                    "kcrown_slider": int(k_crown) if kind == "crown" else int(ss["kcrown_slider"]), "seed_input": int(seed), "greedy_order_select": greedy_order, "gc_step": int(ss["gc_step"])})

settings = Settings(kind, int(n) if kind in ("interval", "random") else C.DEFAULT_N, float(p) if kind == "random" else C.DEFAULT_P, int(k_crown) if kind == "crown" else 4, int(seed), greedy_order)
with st.spinner("Rechne..."):
    a = _analysis(settings)
inst = gs.interval_instance(settings.n, seed=settings.seed) if kind == "interval" else (
    gs.random_conflict_instance(settings.n, settings.p, settings.seed) if kind == "random" else gs.crown_instance(settings.k_crown)[0])

st.markdown("## 🎯 Das Netz und seine Färbung")
kind_label = C.KIND_LABELS[kind]
chi_label = str(a.chi) if a.chi else f"> {C.EXACT_LIMIT} Knoten, nicht berechnet"
st.markdown(f"**{a.n} Knoten, {_german(a.m)} Kanten** ({kind_label}), **ω = {a.omega}, χ = {chi_label}, Δ+1 = {a.delta + 1}**.")
step = st.select_slider("Schritt", options=list(C.STEPS), key="gc_step", format_func=lambda s: C.STEPS[s])

if step == 1:
    algo_options = list(C.ALGOS) + (["interval_greedy"] if kind == "interval" else [])
    algo_labels = {**C.ALGO_LABELS, "interval_greedy": "Greedy nach Startzeit"}
    algo = st.radio("Verfahren", options=algo_options, format_func=lambda v: algo_labels[v], horizontal=True, key="algo_select")
    result = {"greedy": a.greedy, "welsh_powell": a.welsh_powell, "dsatur": a.dsatur, "interval_greedy": a.interval_greedy}[algo]
    n_steps = len(result.events)
    ss["color_k"] = n_steps if "color_k" not in ss else min(max(1, int(ss["color_k"])), n_steps)
    k = st.slider("Färbe-Schritt", 1, n_steps, key="color_k", help="Wie viele Knoten sind schon gefärbt.")
    colors_now = _colors_at_step(result, k)
    current = result.events[k - 1][1]
    if kind == "interval":
        st.plotly_chart(build_timeline(inst, colors_now, current), width="stretch", key=f"s1_timeline_{algo}_{k}")
    else:
        st.plotly_chart(build_network(inst, colors_now, current), width="stretch", key=f"s1_net_{algo}_{k}")
    _, v, c = result.events[k - 1]
    label = inst.labels[v] if inst.labels else str(v)
    st.markdown(f"**Schritt {k} von {n_steps}:** Knoten {label} bekommt Farbe {c}.")
    st.caption(f"Diese Reihenfolge braucht {result.k} Farben.")
elif step == 2:
    if kind == "crown":
        _, bad_order, good_order = gs.crown_instance(k_crown)
        adj = ga.adjacency(inst.n, inst.edges)
        bad_k = ga.greedy_color(adj, bad_order).k
        good_k = ga.greedy_color(adj, good_order).k
        st.plotly_chart(build_good_vs_bad(bad_k, good_k), width="stretch", key="s2_crown")
        st.caption(f"Δ+1 = {a.delta + 1}: die schlechte Reihenfolge (a₀,b₀,a₁,b₁,...) erreicht diese Schranke tatsächlich, obwohl χ = {a.chi} ist.")
    else:
        st.markdown("#### 🔬 Greedy über viele zufällige Reihenfolgen")
        if st.button("200 zufällige Reihenfolgen ausprobieren", key="spread_start"):
            ss["spread_done"] = True
        if ss.get("spread_done"):
            with st.spinner("Rechne..."):
                ks = _order_spread(kind, settings.n, settings.p, settings.k_crown, settings.seed)
            st.plotly_chart(build_order_histogram(ks, a.chi), width="stretch", key="s2_hist")
            st.caption(f"Über 200 zufällige Reihenfolgen: {min(ks)} bis {max(ks)} Farben (χ = {chi_label}).")
elif step == 3:
    st.plotly_chart(build_methods_vs_bounds(a), width="stretch", key="s3_bounds")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("ω (Cliquenzahl)", a.omega, delta_color="off")
    m2.metric("χ (chromatische Zahl)", chi_label, delta_color="off")
    m3.metric("Δ+1", a.delta + 1, delta_color="off")
    m4.metric("DSATUR", a.dsatur.k, delta="Farben", delta_color="off")
    if kind == "interval" and a.chi:
        st.success(f"Greedy nach Startzeit trifft χ exakt: {a.interval_greedy.k} = {a.chi} (immer, auf Intervallgraphen).")
else:
    st.markdown("#### 🔬 Aufwand der exakten Suche")
    if st.button("Über die Größe messen (kann einen Moment dauern)", key="cost_start"):
        ss["cost_done"] = True
    if ss.get("cost_done"):
        with st.spinner("Rechne..."):
            rows_cost = _cost_sweep()
        st.plotly_chart(build_cost_sweep(rows_cost), width="stretch", key="s4_cost")
        st.caption(f"Median über 5 feste Instanzen je Größe (Zufallsgraph, p = {C.DEFAULT_P * 100:.0f} %).")
    st.markdown("#### 🔬 Cliquenüberdeckung gegen χ(G)")
    if st.button("Über die Größe messen", key="cover_start"):
        ss["cover_done"] = True
    if ss.get("cover_done"):
        with st.spinner("Rechne..."):
            rows_cover = _cover_sweep()
        st.plotly_chart(build_cover_vs_chi(rows_cover), width="stretch", key="s4_cover")
        st.caption("Die Cliquenüberdeckung deckt alle Knoten mit möglichst wenigen Cliquen ab (= Färbung des Komplementgraphen); χ(G) selbst färbt G direkt - zwei verschiedene Fragen am selben Graphen.")

st.markdown("---")

st.markdown("## 🎯 Was das Netz verrät")
r1, r2, r3, r4 = st.columns(4)
r1.metric("Cliquenzahl ω", a.omega, delta_color="off")
r2.metric("Chromatische Zahl χ", chi_label, delta_color="off")
r3.metric("Δ+1", a.delta + 1, delta_color="off")
r4.metric("DSATUR-Farben", a.dsatur.k, delta_color="off")

st.markdown("---")

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Greedy ist gut genug** | Die Reihenfolge entscheidet - dieselbe Instanz kann mit schlechter Reihenfolge bis zu Δ+1 statt χ Farben brauchen (Kronengraph). | - |
| **DSATUR ist immer optimal** | Nur auf bestimmten Klassen (z. B. bipartiten Graphen) beweisbar exakt; auf allgemeinen Graphen ist es eine gute Heuristik, kein Beweis. | - |
| **Die exakte Suche ist immer schnell** | Das Backtracking wächst mit der Größe, teils stark - nur bis wenige Dutzend Knoten praktikabel. | - |
| **ω und Δ+1 sind enge Schranken** | Beide können weit von χ entfernt liegen, je nach Graphstruktur. | - |
| **Elementarschritte zeigen den Aufwand** | Sie zählen Knoten- und Kantenbesuche bzw. Backtracking-Versuche, keine Rechenzeit. | - |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Graph.** $G=(V,E)$, $n=|V|$, $m=|E|$. Eine **Färbung** ist eine Abbildung $c: V \to \{0,1,\dots\}$ mit $c(u) \neq c(v)$ für jede Kante $\{u,v\}$. Die **chromatische Zahl** $\chi(G)$ ist die kleinste
Zahl Farben, mit der das gelingt.

**Schranken.** $\omega(G) \le \chi(G) \le \Delta(G) + 1$, wobei $\omega(G)$ die Cliquenzahl (größter vollständiger Teilgraph) und $\Delta(G)$ der Maximalgrad ist.

**Greedy.** In einer Reihenfolge $v_1,\dots,v_n$ erhält $v_i$ die kleinste Farbe, die kein bereits gefärbter Nachbar hat. Reihenfolgeabhängig; im schlechtesten Fall $\Delta+1$ Farben (Kronengraph).

**Welsh-Powell (1967).** Greedy in absteigender Gradreihenfolge.

**DSATUR (Brélaz 1979).** Dynamisch: wähle den ungefärbten Knoten mit größtem Sättigungsgrad (Zahl verschiedener Farben unter gefärbten Nachbarn); Gleichstand nach Restgrad. Beweisbar optimal auf
bipartiten Graphen.

**Intervallgraphen.** Perfekte Graphen: $\chi = \omega$ immer. Greedy nach Startzeit sortiert findet eine $\omega$-Färbung: an jedem Punkt der Zeitachse ist die Zahl gleichzeitig offener Intervalle
höchstens $\omega$, also ist immer eine Farbe frei.

**Cliquenüberdeckung.** Die kleinste Zahl von Cliquen, die $V$ überdecken, ist $\chi(\overline{G})$ (Färbung des Komplementgraphen) - jede Farbklasse einer Komplement-Färbung ist eine Clique in $G$.

**Literatur.** Welsh, D. J. A., & Powell, M. B. (1967). *An upper bound for the chromatic number of a graph and its application to timetabling problems.* The Computer Journal 10(1), 85–86. Brélaz, D.
(1979). *New methods to color the vertices of a graph.* Communications of the ACM 22(4), 251–256.

Implementiert in `gc_algorithm.py` (Greedy, Welsh-Powell, DSATUR, exakte Cliquenzahl/chromatische Zahl, Cliquenüberdeckung), `gc_scenario.py` (Instanzen), `gc_evaluation.py` (Kennzahlen, Sweeps).
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zur Reihe: [Graphen und Netzwerke: BFS bis Cliquenbandbreite](https://sebastianhanisch.net/konzepte-graphen-netzwerke.html)."
)
