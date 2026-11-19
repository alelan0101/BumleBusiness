"""Byg en selvstaendig interaktiv kaldgraf (docs/callgraph.html) med pyan3 og Graphviz.

    python tools/callgraph.py
"""

import html
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = Path(__file__).with_name("callgraph_template.html")
OUTPUT = ROOT / "docs" / "callgraph.html"

SKIP_DIRS = {"tests", "tools", "__pycache__", "docs"}

PALETTE = [
    ("#dbe9fd", "#3b82f6"),
    ("#d9f2e3", "#10b981"),
    ("#fde8d7", "#f97316"),
    ("#ece0fb", "#8b5cf6"),
    ("#fbdce8", "#ec4899"),
    ("#fdf3c9", "#eab308"),
    ("#d8f1f0", "#06b6d4"),
    ("#e6e6ef", "#6366f1"),
    ("#f2e2d8", "#b45309"),
    ("#dcf5d6", "#65a30d"),
    ("#f7dcdc", "#dc2626"),
    ("#d7e3f5", "#1d4ed8"),
    ("#e8e3d8", "#a16207"),
    ("#d9e8e0", "#0d9488"),
    ("#f0ddf0", "#a21caf"),
    ("#e2e8f0", "#475569"),
    ("#f5e6d3", "#c2410c"),
]

VIEWS = [
    {
        "id": "overview",
        "title": "Moduler",
        "caption": "Modulerne i projektet og de kald, der går på tværs af dem. Hver boks er en fil, og pilene viser hvem der kalder hvem.",
        "kind": "modules",
        "rankdir": "LR",
    },
    {
        "id": "full",
        "title": "Fuld graf",
        "caption": "Hele kaldgrafen med moduler, klasser, funktioner og navne. Stiplet kant betyder \"definerer\", optrukket kant betyder \"kalder\".",
        "kind": "all",
        "rankdir": "TB",
    },
    {
        "id": "cli",
        "title": "CLI",
        "caption": "Fra main.main: læs logfilen, parse linjerne, tæl og gruppér, print tabellerne og kør detektionen.",
        "kind": "flow",
        "start": "main__main",
        "depth": 2,
        "rankdir": "LR",
    },
    {
        "id": "dashboard",
        "title": "Dashboard",
        "caption": "visualization.dashboard.create_app er hele Dash-appen: filtrene, de syv faner og callbacken der bygger logtabellen. De næste fem visninger zoomer ind på hver sin fane.",
        "kind": "flow",
        "start": "visualization__dashboard__create_app",
        "depth": 1,
        "skip_names": True,
        "rankdir": "LR",
    },
    {
        "id": "logtabel",
        "title": "Logtabel",
        "caption": "Fane 1: filtrene bygges med logview.filter_options, og callbacken create_app.update_view kalder logview.build_view, der filtrerer, sorterer og bygger tabellen.",
        "kind": "flow",
        "starts": [
            "visualization__dashboard__create_app__update_view",
            "visualization__logview__filter_options",
        ],
        "depth": 2,
        "rankdir": "LR",
    },
    {
        "id": "noegletal",
        "title": "Nøgletal",
        "caption": "Fane 2 (Overblik): periode og fejlrate fra analysis, unikke brugere og IP'er fra aggregation.user_ips, vist med tables.build_columns_table.",
        "kind": "flow",
        "starts": [
            "aggregation__user_ips__get_user_ip_summary",
            "analysis__time_range",
            "analysis__failure_counts",
            "visualization__tables__build_columns_table",
        ],
        "depth": 2,
        "rankdir": "LR",
    },
    {
        "id": "diagrammer",
        "title": "Diagrammer",
        "caption": "Fane 3-6: bar_chart.event_bar_chart til eventtyper, scatter_plots.build_figures til de tre scatter-plots og analysis.hourly_summary til teksten over tid-på-dagen.",
        "kind": "flow",
        "starts": [
            "visualization__bar_chart__event_bar_chart",
            "visualization__scatter_plots__build_figures",
            "analysis__hourly_summary",
        ],
        "depth": 2,
        "rankdir": "LR",
    },
    {
        "id": "fejlandel",
        "title": "Fejlandel",
        "caption": "Fane 7: analysis.port_failure_rows beregner fejlandelen pr. port, og tables.build_columns_table tegner den som tabel.",
        "kind": "flow",
        "starts": [
            "analysis__port_failure_rows",
            "visualization__tables__build_columns_table",
        ],
        "depth": 2,
        "rankdir": "LR",
    },
    {
        "id": "top10",
        "title": "Top 10",
        "caption": "Fane 8: analysis.top_n_lists giver de ti hyppigste brugere, kilde-IP'er og destinationer, som tables.build_top_n_table viser.",
        "kind": "flow",
        "starts": [
            "analysis__top_n_lists",
            "visualization__tables__build_top_n_table",
        ],
        "depth": 2,
        "rankdir": "LR",
    },
    {
        "id": "detect",
        "title": "Detektion",
        "caption": "Fra track_suspicious_accounts: reglerne der finder konti med gentagne advarsler, malware-fund og IP-spor.",
        "kind": "flow",
        "start": "detection__suspicious_accounts__track_suspicious_accounts",
        "depth": 2,
        "rankdir": "LR",
    },
]

NODE_RE = re.compile(r'^"([^"]+)"\s*\[label=')
EDGE_RE = re.compile(r'^"([^"]+)"\s*->\s*"([^"]+)"\s*\[(.*)\];\s*$')
LABEL_RE = re.compile(r'label="((?:[^"\\]|\\.)*)"')
GROUP_RE = re.compile(r'group="(\d+)"')
TOOLTIP_RE = re.compile(r'tooltip="((?:[^"\\]|\\.)*)"')
DEFINES_RE = re.compile(r'style="dashed"')


def source_files():
    files = []
    for path in sorted(ROOT.rglob("*.py")):
        rel = path.relative_to(ROOT)
        if SKIP_DIRS & set(rel.parts[:-1]):
            continue
        files.append(str(path))
    return files


def run_pyan(files):
    with tempfile.TemporaryDirectory() as tmp:
        target = Path(tmp) / "graph.dot"
        command = [sys.executable, "-m", "pyan", *files, "--dot",
                   "--keep-subsumed-edges", "--file", str(target)]
        result = subprocess.run(command, capture_output=True, text=True,
                                encoding="utf-8", errors="replace", cwd=ROOT)
        if result.returncode != 0 or not target.exists():
            sys.exit("pyan3 fejlede. Installér den med: pip install pyan3\n"
                     + (result.stderr or "")[-2000:])
        return target.read_text(encoding="utf-8")


def parse_dot(text):
    nodes = {}
    edges = []
    for line in text.splitlines():
        line = line.strip()
        edge = EDGE_RE.match(line)
        if edge:
            src, dst, attrs = edge.groups()
            edges.append({
                "src": src,
                "dst": dst,
                "dashed": bool(DEFINES_RE.search(attrs)),
            })
            continue
        node = NODE_RE.match(line)
        if not node or 'tooltip=' not in line:
            continue
        name = node.group(1)
        label = LABEL_RE.search(line) or re.search(r'label=(\w+)', line)
        group = GROUP_RE.search(line)
        tooltip = TOOLTIP_RE.search(line)
        tooltip_text = tooltip.group(1) if tooltip else name
        parts = tooltip_text.split("\\n")
        nodes[name] = {
            "id": name,
            "label": f'"{label.group(1)}"',
            "tooltip": f'"{tooltip_text}"',
            "group": group.group(1) if group else None,
            "module": len(parts) == 2,
            "kind": parts[-1] if len(parts) > 2 else "module",
        }
    modules = {n["group"]: n["label"].strip('"') for n in nodes.values() if n["module"]}

    # Samme som dette, måske lettere at læse:
    # modules = {}
    # for n in nodes.values():
    #     if n["module"]:
    #         modules[n["group"]] = n["label"].strip('"')

    return nodes, edges, modules


def reachable(edges, start, depth):
    adjacency = {}
    for edge in edges:
        adjacency.setdefault(edge["src"], set()).add(edge["dst"])
    seen = {start}
    frontier = {start}
    for _ in range(depth):
        following = set()
        for name in frontier:
            following |= adjacency.get(name, set())
        frontier = following - seen
        seen |= frontier
        if not frontier:
            break
    return seen


def view_nodes(view, nodes, edges, modules):
    if view["kind"] == "all":
        return set(nodes), edges
    if view["kind"] == "flow":
        keep = set()
        for start in view.get("starts") or [view["start"]]:
            if start not in nodes:
                sys.exit(f"Ukendt startnode i visningen {view['id']}: {start}")
            keep |= reachable(edges, start, view["depth"])
            keep.add(start)
        if view.get("skip_names", True):
            keep = {name for name in keep if not nodes[name]["kind"].startswith("name in ")}

            # Samme som dette, måske lettere at læse:
            # filtered = set()
            # for name in keep:
            #     if not nodes[name]["kind"].startswith("name in "):
            #         filtered.add(name)
            # keep = filtered

        return keep, [e for e in edges if e["src"] in keep and e["dst"] in keep]

        # Samme som dette, måske lettere at læse:
        # kept_edges = []
        # for e in edges:
        #     if e["src"] in keep and e["dst"] in keep:
        #         kept_edges.append(e)
        # return keep, kept_edges
    return set(), []


def module_graph(nodes, edges, modules):
    names = sorted(modules.values())
    colors = {name: PALETTE[i % len(PALETTE)] for i, name in enumerate(names)}

    # Samme som dette, måske lettere at læse:
    # colors = {}
    # for i, name in enumerate(names):
    #     colors[name] = PALETTE[i % len(PALETTE)]

    node_map = {name: {
        "id": name,
        "label": f'"{name}"',
        "tooltip": f'"{name}"',
        "module": name,
    } for name in names}

    # Samme som dette, måske lettere at læse:
    # node_map = {}
    # for name in names:
    #     node_map[name] = {
    #         "id": name,
    #         "label": f'"{name}"',
    #         "tooltip": f'"{name}"',
    #         "module": name,
    #     }
    pairs = set()
    for edge in edges:
        src = modules.get(nodes.get(edge["src"], {}).get("group"))
        dst = modules.get(nodes.get(edge["dst"], {}).get("group"))
        if src and dst and src != dst:
            pairs.add((src, dst))
    edge_list = [{"src": a, "dst": b, "dashed": False} for a, b in sorted(pairs)]

    # Samme som dette, måske lettere at læse:
    # edge_list = []
    # for a, b in sorted(pairs):
    #     edge_list.append({"src": a, "dst": b, "dashed": False})
    return node_map, edge_list, colors


def node_module(node, modules):
    return modules.get(node["group"]) or node["label"].strip('"')


def to_dot(node_map, edge_list, colors, rankdir):
    lines = [
        "digraph G {",
        f'  graph [rankdir={rankdir}, ranksep=0.55, nodesep=0.3, pad=0.2, '
        'fontname="Segoe UI", bgcolor="transparent"];',
        '  node [shape=box, style="rounded,filled", fontname="Segoe UI", fontsize=13, '
        'fontcolor="#1f2937", penwidth=1.2, margin="0.12,0.06", height=0.36];',
        '  edge [color="#9aa1ab", arrowsize=0.65, penwidth=1.0];',
    ]
    for name, node in node_map.items():
        fill, stroke = colors[node["module"]]
        cls = "m" + re.sub(r"\W", "_", node["module"])
        lines.append(
            f'  "{name}" [label={node["label"]}, tooltip={node["tooltip"]}, '
            f'fillcolor="{fill}", color="{stroke}", class="{cls}"];'
        )
    for edge in edge_list:
        style = 'style="dashed"' if edge["dashed"] else 'style="solid"'
        lines.append(f'  "{edge["src"]}" -> "{edge["dst"]}" [{style}];')
    lines.append("}")
    return "\n".join(lines)


def to_svg(dot_text):
    dot = shutil.which("dot")
    if not dot:
        sys.exit("Graphviz mangler. Installér det med: scoop install graphviz")
    result = subprocess.run([dot, "-Tsvg"], input=dot_text.encode("utf-8"),
                            capture_output=True)
    if result.returncode != 0:
        sys.exit("Graphviz kunne ikke tegne grafen:\n"
                 + result.stderr.decode("utf-8", "replace"))
    svg = result.stdout.decode("utf-8")
    svg = re.sub(r"<\?xml[^>]*\?>\s*", "", svg)
    svg = re.sub(r"<!DOCTYPE[^>]*>\s*", "", svg, flags=re.IGNORECASE)
    svg = re.sub(r"<!--[^>]*-->\s*", "", svg)
    return svg.strip()


def build():
    nodes, edges, modules = parse_dot(run_pyan(source_files()))
    if not modules:
        sys.exit("Kunne ikke finde moduler i kaldgrafen")
    module_colors = {name: PALETTE[i % len(PALETTE)]
                     for i, name in enumerate(sorted(modules.values()))}

    # Samme som dette, måske lettere at læse:
    # module_colors = {}
    # for i, name in enumerate(sorted(modules.values())):
    #     module_colors[name] = PALETTE[i % len(PALETTE)]

    sections = []
    for view in VIEWS:
        if view["kind"] == "modules":
            node_map, edge_list, colors = module_graph(nodes, edges, modules)
        else:
            keep, edge_list = view_nodes(view, nodes, edges, modules)
            node_map = {name: {**nodes[name], "module": node_module(nodes[name], modules)}
                        for name in nodes if name in keep}

            # Samme som dette, måske lettere at læse:
            # node_map = {}
            # for name in nodes:
            #     if name in keep:
            #         node_map[name] = {
            #             **nodes[name],
            #             "module": node_module(nodes[name], modules),
            #         }
            colors = module_colors
        svg = to_svg(to_dot(node_map, edge_list, colors, view["rankdir"]))
        sections.append(f"""
    <section class="view" data-view="{view['id']}" hidden>
      <p class="caption">{html.escape(view['caption'])}</p>
      <div class="canvas">{svg}</div>
    </section>""")

    tabs = "\n".join(
        '      <button data-view="%s"%s>%s</button>' % (
            v["id"], ' class="active"' if i == 0 else "", v["title"])
        for i, v in enumerate(VIEWS)
    )

    # Samme som dette, måske lettere at læse:
    # buttons = []
    # for i, v in enumerate(VIEWS):
    #     buttons.append(
    #         '      <button data-view="%s"%s>%s</button>' % (
    #             v["id"], ' class="active"' if i == 0 else "", v["title"])
    #     )
    # tabs = "\n".join(buttons)
    chips = "\n".join(
        f'      <button class="chip" data-class="m{re.sub(r"[^0-9a-zA-Z_]", "_", name)}">'
        f'<span style="background:{module_colors[name][1]}"></span>'
        f'{html.escape(name)}</button>'
        for name in sorted(module_colors)
    )

    # Samme som dette, måske lettere at læse:
    # buttons = []
    # for name in sorted(module_colors):
    #     buttons.append(
    #         f'      <button class="chip" data-class="m{re.sub(r"[^0-9a-zA-Z_]", "_", name)}">'
    #         f'<span style="background:{module_colors[name][1]}"></span>'
    #         f'{html.escape(name)}</button>'
    #     )
    # chips = "\n".join(buttons)

    page = Template(TEMPLATE.read_text(encoding="utf-8")).substitute(
        tabs=tabs,
        chips=chips,
        views="".join(sections),
    )
    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(page, encoding="utf-8")
    print(f"Skrev {OUTPUT.relative_to(ROOT)} ({OUTPUT.stat().st_size // 1024} kB, "
          f"{len(VIEWS)} visninger)")


if __name__ == "__main__":
    build()
