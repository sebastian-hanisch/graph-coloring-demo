"""Plotly-Figuren: Zeitachse (Intervallgraph), Netzwerk-Layout (Zufallsgraph/Kronengraph), Reihenfolge-Histogramm, Schranken-Balken, Aufwandskurve."""

import math

import plotly.graph_objects as go

TEAL, ORANGE, BLUE, RED, GREY, LIGHT = "#2F6B65", "#f58518", "#4c78a8", "#e45756", "#b7bec7", "#e8ebee"
PALETTE = (TEAL, ORANGE, BLUE, RED, "#54a24b", "#b279a2", "#9d755d", "#eeca3b", "#72b7b2", "#ff9da6")


def _color_for(c):
    return PALETTE[c % len(PALETTE)] if c >= 0 else LIGHT


def circular_layout(n):
    return [(math.cos(2 * math.pi * i / n), math.sin(2 * math.pi * i / n)) for i in range(n)]


def _base_layout(fig, height=380, title=None):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=30 if title else 10, b=10), showlegend=False, plot_bgcolor="white",
                       title=dict(text=title, x=0.01, font=dict(size=13)) if title else None)
    return fig


# --- Intervallgraph: Zeitachse -------------------------------------------------------------------------------------------------------------------


def build_timeline(inst, colors_at_step, current=None, labels=None):
    """Waagerechte Balken je Lieferung (Zeitfenster), eingefärbt nach der bisherigen Zuweisung (`colors_at_step`, -1 = noch nicht gefärbt); Zeilen nach Startzeit sortiert."""
    order = sorted(range(inst.n), key=lambda v: inst.intervals[v][0])
    fig = go.Figure()
    for row, v in enumerate(order):
        s, e = inst.intervals[v]
        c = colors_at_step[v]
        col = _color_for(c) if c >= 0 else LIGHT
        line_width = 14 if v != current else 20
        fig.add_trace(go.Scatter(x=[s, e], y=[row, row], mode="lines", line=dict(color=col, width=line_width),
                                  hovertext=f"{labels[v] if labels else v}: [{s:.1f}, {e:.1f})" + (f" – Farbe {c}" if c >= 0 else ""), hoverinfo="text"))
    fig.update_layout(height=max(220, 24 * inst.n), margin=dict(l=10, r=10, t=10, b=30), showlegend=False, plot_bgcolor="white")
    fig.update_xaxes(fixedrange=True, title="Zeit", gridcolor=LIGHT)
    fig.update_yaxes(fixedrange=True, visible=False, autorange="reversed")
    return fig


# --- Netzwerk-Layout (Zufallsgraph, Kronengraph) --------------------------------------------------------------------------------------------------


def build_network(inst, colors_at_step, current=None, height=380):
    xy = dict(zip(range(inst.n), circular_layout(inst.n)))
    fig = go.Figure()
    ex, ey = [], []
    for u, v in inst.edges:
        ex += [xy[u][0], xy[v][0], None]
        ey += [xy[u][1], xy[v][1], None]
    fig.add_trace(go.Scatter(x=ex, y=ey, mode="lines", line=dict(color=GREY, width=1.2), hoverinfo="skip"))
    node_colors = [_color_for(c) for c in colors_at_step]
    sizes = [16 if v == current else 12 for v in range(inst.n)]
    line_colors = ["black" if v == current else "white" for v in range(inst.n)]
    labels = [inst.labels[v] if inst.labels else str(v) for v in range(inst.n)]
    fig.add_trace(go.Scatter(x=[xy[v][0] for v in range(inst.n)], y=[xy[v][1] for v in range(inst.n)], mode="markers+text", text=labels, textposition="top center",
                              marker=dict(size=sizes, color=node_colors, line=dict(color=line_colors, width=2))))
    fig.update_xaxes(visible=False, fixedrange=True, scaleanchor="y", scaleratio=1)
    fig.update_yaxes(visible=False, fixedrange=True)
    return _base_layout(fig, height)


# --- Reihenfolge-Histogramm ------------------------------------------------------------------------------------------------------------------------


def build_order_histogram(ks, chi=None):
    fig = go.Figure(go.Histogram(x=ks, marker_color=TEAL, xbins=dict(size=1)))
    if chi:
        fig.add_vline(x=chi, line=dict(color=RED, dash="dash", width=2), annotation_text=f"χ = {chi}", annotation_position="top")
    fig.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10), showlegend=False, plot_bgcolor="white", bargap=0.1)
    fig.update_xaxes(fixedrange=True, title="benutzte Farben")
    fig.update_yaxes(fixedrange=True, title="Häufigkeit", gridcolor=LIGHT)
    return fig


def build_good_vs_bad(bad_k, good_k):
    fig = go.Figure(go.Bar(x=["schlechte Reihenfolge", "gute Reihenfolge"], y=[bad_k, good_k], marker_color=[RED, TEAL], text=[bad_k, good_k], textposition="outside"))
    fig.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10), showlegend=False, plot_bgcolor="white")
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True, title="benutzte Farben", gridcolor=LIGHT)
    return fig


# --- Verfahren gegen Schranken ----------------------------------------------------------------------------------------------------------------------


def build_methods_vs_bounds(a):
    names = ["Greedy", "Welsh-Powell", "DSATUR"]
    values = [a.greedy.k, a.welsh_powell.k, a.dsatur.k]
    if a.interval_greedy:
        names.append("Greedy (Startzeit)")
        values.append(a.interval_greedy.k)
    top = max(values + [a.delta + 1, a.chi or 0]) * 1.2
    fig = go.Figure(go.Bar(x=names, y=values, marker_color=TEAL, text=values, textposition="outside"))
    if a.chi:
        fig.add_hline(y=a.chi, line=dict(color=RED, width=2), annotation_text=f"χ = {a.chi}", annotation_position="top left")
    fig.add_hline(y=a.omega, line=dict(color=BLUE, dash="dot", width=1.5), annotation_text=f"ω = {a.omega}", annotation_position="bottom left")
    fig.add_hline(y=a.delta + 1, line=dict(color=GREY, dash="dot", width=1.5), annotation_text=f"Δ+1 = {a.delta + 1}", annotation_position="top right")
    fig.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10), showlegend=False, plot_bgcolor="white")
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True, title="benutzte Farben", gridcolor=LIGHT, range=[0, top], autorange=False)
    return fig


# --- Aufwand und Cliquenüberdeckung -----------------------------------------------------------------------------------------------------------------


def build_cost_sweep(rows):
    ns = [r["n"] for r in rows]
    fig = go.Figure(go.Scatter(x=ns, y=[r["steps"] for r in rows], mode="lines+markers", line=dict(color=TEAL, width=2)))
    fig.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10), showlegend=False, plot_bgcolor="white")
    fig.update_xaxes(fixedrange=True, title="Knotenzahl n", gridcolor=LIGHT)
    fig.update_yaxes(fixedrange=True, title="Elementarschritte (exakte Suche)", type="log", gridcolor=LIGHT)
    return fig


def build_cover_vs_chi(rows):
    ns = [r["n"] for r in rows]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ns, y=[r["cover"] for r in rows], mode="lines+markers", name="Cliquenüberdeckung", line=dict(color=ORANGE, width=2)))
    fig.add_trace(go.Scatter(x=ns, y=[r["chi"] for r in rows], mode="lines+markers", name="χ(G)", line=dict(color=TEAL, width=2)))
    fig.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10), showlegend=True, legend=dict(x=0.02, y=0.98), plot_bgcolor="white")
    fig.update_xaxes(fixedrange=True, title="Knotenzahl n", gridcolor=LIGHT)
    fig.update_yaxes(fixedrange=True, title="Zahl der Klassen", gridcolor=LIGHT)
    return fig
