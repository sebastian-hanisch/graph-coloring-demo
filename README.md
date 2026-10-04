# Graphfärbung – Greedy, Welsh-Powell, DSATUR, exakt – Streamlit-Demo

**[→ Demo live ausprobieren](https://sebastianhanisch-graph-coloring-demo.streamlit.app/)**

Fünftes Stück der **Graphen-und-Netzwerke-Reihe** der "Konzepte"-Reihe für die Website "Sebastian Hanisch – Operations Research und Machine Learning", Kind der Durchmusterung ([bfs-dfs-demo](https://github.com/sebastian-hanisch/bfs-dfs-demo)). Eine **Knotenfärbung** weist jedem Knoten eine Farbe zu, sodass keine zwei benachbarten Knoten dieselbe Farbe haben; die **chromatische Zahl** χ(G) ist die kleinste Farbenzahl, mit der das gelingt. Klassische Schranken: **ω(G) ≤ χ(G) ≤ Δ(G) + 1** (Cliquenzahl, Maximalgrad). **Greedy** (feste Reihenfolge, kleinste freie Farbe je Knoten) ist *reihenfolgeabhängig*: dieselbe Instanz kann mit verschiedenen Reihenfolgen sehr unterschiedlich viele Farben brauchen. **Welsh-Powell** (1967, Grad absteigend) und **DSATUR** (Brélaz 1979, Sättigungsgrad) sind zwei feste Strategien dagegen; eine **exakte** Suche (Backtracking mit der Cliquenzahl als untere Schranke) findet χ selbst für kleine Graphen. Bei **Intervallgraphen** ist Greedy nach Startzeit sortiert beweisbar optimal; beim **Kronengraphen** zeigt eine schlechte Reihenfolge das Gegenteil.

**Einordnung in die Reihe:** die Reihe hat zwölf Stücke, dies ist das fünfte (Details in `graphen-planung/PLAN.md` des Portfolio-Ordners):

```
1 BFS und DFS (Wurzel)                                                        [gebaut: bfs-dfs-demo]
 ├─ 2 Brücken und Artikulationspunkte ─ 4 Euler-Touren                        [gebaut: bridges-demo, euler-tour-demo]
 ├─ 3 Starke Zusammenhangskomponenten, topologische Sortierung                [gebaut: scc-demo]
 ├─ 5 Graphfärbung                                                            [DIESES STÜCK]
 ├─ 6 Zentralität ─ 7 Strukturkennzahlen                                      [nicht gebaut]
 │        ├─ 8 Robustheit ─ 9 Kaskaden und Ausbreitung                        [nicht gebaut]
 │        └─ 10 Kritische Knoten härten                                       [nicht gebaut]
 └─ 11 Bandbreite ─ 12 Bandbreite von G(n,k,b) und Cliquenüberdeckung         [nicht gebaut]
```

Ergebnis in Kürze: **DSATUR trifft die chromatische Zahl auf Zufallsgraphen fast immer exakt, aber nicht beweisbar – bei dichteren Instanzen (n = 30, 50 % Kantenwahrscheinlichkeit) fanden wir eine Instanz, an der DSATUR 9 statt χ = 8 Farben braucht (Welsh-Powell und einfaches Greedy sogar 10).** Auf Intervallgraphen dagegen trifft Greedy nach Startzeit sortiert χ **beweisbar** immer exakt – in über 500 gemessenen Instanzen ausnahmslos. Der Kronengraph zeigt das Gegenteil in Reinform: bipartit (χ = 2), aber eine ungünstige Reihenfolge zwingt Greedy zur oberen Schranke Δ+1 (bis zu 8 statt 2 Farben bei k = 8). Ein einzelner Zufallsgraph (n = 20, chi = 5) braucht über 200 zufällige Reihenfolgen zwischen 5 und 7 Farben – derselbe Graph, dieselbe Regel, unterschiedliches Ergebnis.

## Warum dieses Problem

Wie viele Rampen braucht ein Verteilzentrum, damit sich keine zwei Lieferungen mit überlappenden Zeitfenstern dieselbe Rampe teilen? Wie viele Zeitslots, damit keine zwei Kurse mit gemeinsamen Teilnehmern kollidieren? Das ist Graphfärbung: Konfliktknoten dürfen nicht dieselbe Ressource (Farbe) bekommen. Die Demo zeigt, dass die naheliegendste Lösung (Greedy) tückisch reihenfolgeabhängig ist, dass zwei klassische Verbesserungen (Welsh-Powell, DSATUR) meist, aber nicht beweisbar helfen, und dass es eine Graphklasse gibt (Intervallgraphen), auf der die einfachste Idee bewiesen optimal ist.

Abgrenzung: eine **Cliquenüberdeckung** (kleinste Zahl von Cliquen, die alle Knoten überdecken) ist genau die Färbung des **Komplementgraphen** – die Brücke zu Stück 12 (Bandbreite von G(n,k,b) und Cliquenüberdeckung), hier nur kurz gezeigt, nicht vertieft.

## Vorab-Hypothesen (vor der Messung notiert, hier geprüft)

| Hypothese | Ergebnis |
|---|---|
| **H1** Greedy ist reihenfolgeabhängig; im schlechtesten Fall erreicht es Δ+1 Farben, obwohl χ viel kleiner ist. | ✅ Bestätigt am Kronengraphen (Satz, von Hand nachgerechnet): die Reihenfolge a₀,b₀,a₁,b₁,... zwingt Greedy zu k Farben bei χ = 2 und Δ+1 = k – die Schranke wird tatsächlich erreicht, nicht nur theoretisch möglich. |
| **H2** Welsh-Powell und DSATUR liegen auf Zufallsgraphen näher an χ als einfaches Greedy. | ✅ Bestätigt: bei n = 30 (p = 0.3) braucht Greedy im Median das 1.4-Fache von χ, Welsh-Powell das 1.2-Fache, DSATUR das 1.0-Fache (trifft χ in dieser Stichprobe immer). |
| **H3** DSATUR ist immer optimal. | ❌ **Widerlegt – bewusst gesucht, nicht angenommen:** bei n = 30, 50 % Kantenwahrscheinlichkeit fanden wir eine Instanz mit χ = 8, an der DSATUR 9 Farben braucht (Median-Verhältnis über 5 Instanzen: 1.125). DSATUR ist beweisbar nur auf bestimmten Klassen exakt (hier: bipartite Graphen, s. u.), nicht allgemein. |
| **H4** Intervallgraphen: Greedy nach Startzeit trifft χ immer exakt. | ✅ Bestätigt als Satz, nicht nur Beobachtung: 100 % Treffer auf über 500 gemessenen Intervallgraph-Instanzen (n = 8 bis 25). Intervallgraphen sind perfekte Graphen (χ = ω), und an jedem Zeitpunkt ist höchstens ω Intervalle gleichzeitig offen – eine Farbe ist immer frei. |
| **H5** DSATUR ist auf bipartiten Graphen beweisbar optimal (≤ 2 Farben). | ✅ Bestätigt: 100 % auf 100 gemessenen Zufalls-Bipartitgraphen (verschiedene Größen). |
| **H6** ω und Δ+1 sind meist enge Schranken für χ. | ❌ **Teilweise widerlegt:** ω trifft χ auf Zufallsgraphen oft (z. B. n=10: 3=3, n=25: 5=5), aber Δ+1 liegt regelmäßig weit darüber (n=20: χ=4 gegen Δ+1=10, mehr als das Doppelte). |

## Befunde (gemessen, keine Behauptungen)

Median über 5 feste Instanzen (Seeds 100000–100004), Zufallsgraph mit 30 % Kantenwahrscheinlichkeit, sofern nicht anders angegeben; alle Verfahren sind deterministisch, die Instanzen kommen aus Python-`random` mit festem Seed.

| Frage | Ergebnis |
|---|---|
| **Stimmt das Verfahren?** | ✅ Jede Färbung (Greedy, Welsh-Powell, DSATUR, exakt) ist gültig; χ stimmt gegen Brute-Force (n ≤ 8) und bekannte Graphen (Kₙ → n, ungerade Kreise → 3, gerade Kreise → 2, Petersen-Graph → 3) überein; ω stimmt gegen Brute-Force überein |
| **Lücke gegen χ (Zufallsgraph)** | Greedy/Welsh-Powell/DSATUR gegen χ: **1.0/1.0/1.0** (n=10) bis **1.4/1.2/1.0** (n=30) |
| **Schranken (Zufallsgraph)** | ω/χ/Δ+1: **3/3/5** (n=10), **4/4/9** (n=15), **3/4/10** (n=20), **5/5/14** (n=25), **5/5/15** (n=30) |
| **Intervallgraph-Satz** | Greedy nach Startzeit == χ in **100 %** von über 500 Instanzen (n = 8–25) |
| **DSATUR auf Bipartitgraphen** | ≤ 2 Farben in **100 %** von 100 Instanzen |
| **Aufwand der exakten Suche** (Elementarschritte) | **31 / 52 / 129 / 117 / 464 / 3961 / 6133** bei n = 10/15/20/25/30/35/40 |
| **Cliquenüberdeckung gegen χ(G)** | **5/3** (n=10), **7/4** (n=15), **9/4** (n=20), **9/5** (n=25), **10/5** (n=30) – die Überdeckung braucht durchweg mehr Cliquen als χ(G) Farben |

Presets (6), alle mit den Zahlen in ihren Hilfetexten (`tests/test_presets.py`):

| Preset | Was es zeigt |
|---|---|
| Kronengraph (Lehrbuch) | 8 Knoten (k=4), bipartit: χ=2. Die schlechte Reihenfolge (a₀,b₀,a₁,b₁,...) zwingt Greedy zu 4 Farben (= Δ+1) |
| Intervallgraph (Standardfall) | 16 Lieferzeitfenster, 40 Überlappungen: ω = χ = 6, Greedy nach Startzeit trifft es exakt |
| Intervallgraph dicht | 30 Lieferzeitfenster, 138 Überlappungen: ω = χ = 11, weiterhin exakt |
| Zufallsgraph: Reihenfolge entscheidet | 20 Knoten, χ = 5: über 200 zufällige Reihenfolgen braucht Greedy zwischen 5 und 7 Farben |
| Zufallsgraph dicht (DSATUR-Lücke) | 30 Knoten, 248 Kanten: χ = 8, aber DSATUR braucht 9 Farben (Welsh-Powell/Greedy sogar 10) |
| Aufwand und Cliquenüberdeckung | Exakte Suche: 31 (n=10) bis 6133 (n=40) Elementarschritte; Cliquenüberdeckung 10 gegen χ(G) = 5 bei n=30 |

## Modell und Verfahren

- **Instanz** (`gc_scenario.py`): der **Intervallgraph** modelliert Lieferzeitfenster an einem Verteilzentrum – zwei Lieferungen kollidieren, wenn sich ihre Zeitfenster überlappen (immer ein *perfekter Graph*: χ = ω). Der **Zufalls-Konfliktgraph** G(n,p) hat beliebige paarweise Konflikte ohne Intervallstruktur. Das Lehrbuchbeispiel **Kronengraph** (2k Knoten, Kante aᵢ-bⱼ für alle i≠j) ist bipartit, aber jeder Knoten hat Grad k−1 – das Δ+1-Worst-Case für Greedy wird hier tatsächlich erreicht.
- **Greedy** (`gc_algorithm.greedy_color`): je Knoten in einer gegebenen Reihenfolge die kleinste Farbe, die kein bereits gefärbter Nachbar hat.
- **Welsh-Powell** (1967): Greedy in absteigender Gradreihenfolge.
- **DSATUR** (Brélaz 1979): dynamisch – wiederholt der ungefärbte Knoten mit größtem **Sättigungsgrad** (Zahl verschiedener Farben unter bereits gefärbten Nachbarn) gewählt, Gleichstand nach Restgrad.
- **Exakte chromatische Zahl** (`chromatic_number`): Backtracking-Suche, beginnend bei der **Cliquenzahl** ω(G) als untere Schranke, mit Farbsymmetrie-Abbruch (eine neue Farbe wird nur probiert, wenn sie höchstens die bisher größte benutzte + 1 ist). Nur bis 35 Knoten praktikabel (`EXACT_LIMIT`).
- **Cliquenzahl** (`clique_number`): Branch-and-Bound (Einschließen/Ausschließen je Kandidat), gegen Brute-Force geprüft.
- **Cliquenüberdeckung** (`clique_cover_dsatur`): DSATUR auf dem **Komplementgraphen** – jede Farbklasse dieser Färbung ist eine Clique im Original.
- **Elementarschritte:** jeder gefärbte/besuchte Knoten und jede von einem Ende angesehene Kante zählt 1; die exakte Suche zählt zusätzlich jeden Backtracking-Versuch. Ein Näherungsmaß, keine Laufzeit.

## Was die App zeigt

1. **Vier Schritte** (Schritt-Regler): **Greedy in Aktion** (Verfahrenswahl, Regler über die Färbe-Schritte, Zeitachse beim Intervallgraphen bzw. Netzwerk-Layout sonst) → **Reihenfolge entscheidet** (Kronengraph: gute gegen schlechte Reihenfolge direkt; sonst: Histogramm über 200 zufällige Reihenfolgen) → **Wer kommt am nächsten an χ?** (Balken Greedy/Welsh-Powell/DSATUR gegen die Schranken ω und Δ+1) → **Aufwand und Cliquenüberdeckung** (auf Abruf: Aufwand der exakten Suche über die Größe; Cliquenüberdeckung gegen χ(G) selbst).
2. Regler: Instanz (Intervallgraph / Zufallsgraph / Kronengraph), je nach Instanz: Knotenzahl, Kantenwahrscheinlichkeit, Knoten je Seite (Kronengraph); Reihenfolge für Greedy (aufsteigend/gemischt bzw. gut/schlecht beim Kronengraphen); Zufalls-Seed (+🎲); Permalink in der Adresszeile.

## Was nicht funktioniert hat / Grenzen

- **H3 und H6 widerlegt.** DSATUR ist keine bewiesene Garantie auf allgemeinen Graphen – nur eine sehr gute Heuristik, mit einer gefundenen Gegenprobe; Δ+1 ist oft eine sehr lockere obere Schranke.
- **Exakte Suche nur bis ~35 Knoten.** Backtracking wächst mit der Größe, teils stark (bis zu 6133 Schritte bei n=40 im Median, Ausreißer deutlich mehr); keine LP-Relaxation oder SAT-basierte Verfahren.
- **Cliquenüberdeckung nur als Brücke gezeigt.** Die Demo berechnet sie über DSATUR auf dem Komplementgraphen (eine Heuristik, kein Beweis der Optimalität) – eine Vertiefung folgt in Stück 12.
- **Elementarschritte statt Laufzeit.** Die gemessenen Faktoren gelten für das Zählmaß, echte Laufzeiten hängen an der Implementierung.
- **Synthetische Instanzen.** Intervallgraph und Zufallsgraph sind erzeugt, keine echten Lieferpläne oder Konfliktdaten.

## Tests

`tests/test_algorithm.py` (Gültigkeit aller Verfahren, χ gegen Brute-Force und bekannte Graphen, ω≤χ≤Δ+1, Intervallgraph-Satz auf 150 Instanzen, DSATUR auf Bipartitgraphen auf 100 Instanzen, Kronengraph von Hand, Cliquenüberdeckungs-Äquivalenz, Buchführung, Sonderfälle), `tests/test_scenario.py`, `tests/test_evaluation.py`, `tests/test_presets.py` (jede Zahl der Hilfetexte), `tests/test_claims.py` (jede README-Zahl über die echten Auswertungsfunktionen), `tests/test_app.py` (37: AppTest – Voreinstellung, jedes Preset, jeder Schritt für jede Instanz, jede Position des Färbe-Schritt-Reglers, Randwerte, Permalink-Grenzen, bedingte Regler, Berechnungen auf Abruf, Footer). 91 Tests insgesamt.

```
python -m pytest tests/ -v
```

## Dateistruktur

| Datei | Inhalt |
|---|---|
| `app.py` | Streamlit-App |
| `gc_algorithm.py` | Greedy, Welsh-Powell, DSATUR, exakte Cliquenzahl/chromatische Zahl, Cliquenüberdeckung |
| `gc_scenario.py` | Intervallgraph, Zufallsgraph, Kronengraph, Zufalls-Bipartitgraph |
| `gc_evaluation.py` | Analyse, Sweeps (Lücke gegen χ, Schranken, Aufwand, Cliquenüberdeckung) |
| `gc_visualization.py` | Plotly-Figuren (Zeitachse, Netzwerk-Layout, Histogramm, Schranken-Balken) |
| `gc_presets.py`, `gc_constants.py` | Permalink, Presets, gemessene Werte |
| `tests/` | Tests |

## Bewusst nicht umgesetzt

Zentralität, Strukturkennzahlen, Robustheit und Kaskaden, kritische Knoten härten, Bandbreite – eigene Stücke der Reihe. Cliquenüberdeckung nur als Brücke, keine eigene Vertiefung (Stück 12).

## Lokal ausführen

```
python -m venv venv
venv\Scripts\pip install -r requirements-dev.txt
venv\Scripts\streamlit run app.py
```

## Literatur

- Welsh, D. J. A., & Powell, M. B. (1967). *An upper bound for the chromatic number of a graph and its application to timetabling problems.* The Computer Journal 10(1), 85–86.
- Brélaz, D. (1979). *New methods to color the vertices of a graph.* Communications of the ACM 22(4), 251–256.

Gebaut mit Streamlit, Plotly, NumPy und pandas.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zur Reihe: [Graphen und Netzwerke: BFS bis Cliquenbandbreite](https://sebastianhanisch.net/konzepte-graphen-netzwerke.html).
