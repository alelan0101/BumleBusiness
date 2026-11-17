"""Dash-dashboard med logtabel, overblik, diagrammer og top-10."""

from dash import Dash, Input, Output, dcc, html

import analysis
from aggregation import user_ips
from errors import DashboardError

from . import bar_chart, logview, scatter_plots, tables

DEFAULT_PORT = 8050

# CSS-grid til filtrene og til top-10-tabellerne, så de fordeler sig efter skærmbredden
FILTER_GRID = "repeat(auto-fit, minmax(120px, 1fr))"
TOP_N_GRID = "repeat(auto-fit, minmax(280px, 1fr))"


# Bygger hele Dash-appen: fanerne, filtrene, tabellerne og diagrammerne.
# Funktionen kaldes af run() nedenfor og returnerer den app der skal startes.
def create_app(records) -> Dash:
    columns = list(tables.DEFAULT_COLUMNS)

    # Der laves et dropdown-filter pr. attribut i FILTER_ATTRIBUTES. Hvert filter får et id som callbacken nederst i funktionen kan slå op i.
    filter_dropdowns = [
        html.Div(
            [
                html.Label(tables.COLUMN_LABELS[attribute]),
                dcc.Dropdown(
                    id=f"{attribute}-filter",
                    options=[
                        {"label": value, "value": value}
                        for value in logview.filter_options(records, attribute)
                    ],
                    placeholder="Alle",
                    clearable=True,
                ),
            ]
        )
        for attribute in logview.FILTER_ATTRIBUTES
    ]

    # Fritekstsøgning, der kun ser på besked-kolonnen
    msg_filter = html.Div(
        [
            html.Label(tables.COLUMN_LABELS["msg"]),
            dcc.Input(
                id="msg-filter",
                type="text",
                placeholder="Søg i besked",
                debounce=True,
            ),
        ]
    )

    # To dropdowns: hvilken kolonne der sorteres efter, og om det er stigende eller faldende
    sort_controls = [
        html.Div(
            [
                html.Label("Sorter efter"),
                dcc.Dropdown(
                    id="sort-column",
                    options=[
                        {
                            "label": tables.COLUMN_LABELS[column],
                            "value": column,
                        }
                        for column in columns
                    ],
                    value=logview.DEFAULT_SORT_COLUMN,
                    clearable=False,
                ),
            ]
        ),
        html.Div(
            [
                html.Label("Retning"),
                dcc.Dropdown(
                    id="sort-direction",
                    options=[
                        {"label": "Stigende", "value": "asc"},
                        {"label": "Faldende", "value": "desc"},
                    ],
                    value="asc",
                    clearable=False,
                ),
            ]
        ),
    ]

    # Figurerne bygges en gang her, så de ikke skal regnes ud hver gang dashboardet åbnes i browseren
    figure = logview.build_view(records)[0]
    charts = scatter_plots.build_figures(records)

    # Fane 1: selve logtabellen med filtre og sortering
    table_tab = dcc.Tab(
        label="Logtabel",
        value="table",
        children=[
            html.Div(
                filter_dropdowns + [msg_filter] + sort_controls,
                style={
                    "display": "grid",
                    "gridTemplateColumns": FILTER_GRID,
                    "gap": "12px",
                    "marginTop": "12px",
                },
            ),
            html.Div(html.Span(id="row-count"), style={"margin": "16px 0"}),
            dcc.Graph(id="log-table", figure=figure),
        ],
    )

    # Tallene til overbliksfanen: periode, fejlrate og unikke brugere/IP'er
    summary = user_ips.get_user_ip_summary(records)
    ips_per_user = summary["ips_per_user"]
    ip_counts = [str(count) for count in ips_per_user.values()]
    first, last = analysis.time_range(records)
    failures, total = analysis.failure_counts(records)
    failure_text = (
        f"{failures} af {total} ({failures / total * 100:.1f} %)"
        if total
        else "Ingen data"
    )
    period_text = (
        f"{first:%Y-%m-%d %H:%M:%S} – {last:%Y-%m-%d %H:%M:%S}"
        if first
        else "Ingen data"
    )

    # Fane 2: nøgletal for hele loggen plus en tabel over IP'er pr. bruger
    overview_tab = dcc.Tab(
        label="Overblik",
        children=[
            html.Div(
                [
                    html.Div(
                        [
                            html.P(f"Periode: {period_text}"),
                            html.P(f"Fejlrate: {failure_text}"),
                            html.P(f"Unikke brugere: {summary['user_count']}"),
                            html.P(
                                f"Unikke IP'er: {summary['unique_ip_count']}"
                            ),
                        ],
                        style={"marginTop": "12px"},
                    ),
                    dcc.Graph(
                        figure=tables.build_columns_table(
                            ("Bruger", "Unikke IP'er"),
                            [list(ips_per_user), ip_counts],
                        )
                    ),
                ],
                style={
                    "display": "grid",
                    "gridTemplateColumns": TOP_N_GRID,
                    "gap": "12px",
                },
            )
        ],
    )

    # Teksten over det første diagram: gennemsnit pr. time og den time med flest/færrest events
    hourly = analysis.hourly_summary(records)
    hourly_text = (
        f"Gennemsnit: {hourly['average']:.1f} events pr. time. "
        f"Flest kl. {hourly['busiest_hour']:02d} "
        f"({hourly['busiest_count']}), færrest kl. "
        f"{hourly['quietest_hour']:02d} ({hourly['quietest_count']})."
        if hourly["busiest_hour"] is not None
        else "Ingen data at vise"
    )

    # Fane 3-6: diagrammerne, hver i sin egen tab
    chart_tabs = [
        dcc.Tab(
            label="Eventtyper",
            children=[dcc.Graph(figure=bar_chart.event_bar_chart(records))],
        ),
        dcc.Tab(
            label="Tid på dagen",
            children=[
                html.P(hourly_text, style={"margin": "12px 0 0"}),
                dcc.Graph(figure=charts["events_by_hour"]),
            ],
        ),
        dcc.Tab(
            label="Fejl pr. bruger",
            children=[dcc.Graph(figure=charts["user_failure_rate"])],
        ),
        dcc.Tab(
            label="Port og eventtype",
            children=[dcc.Graph(figure=charts["port_event"])],
        ),
    ]

    # Tallene til fane 6: fejlandel pr. port, både for alle og for eksterne IP'er
    port_rows = analysis.port_failure_rows(records)

    # Fane 6: fejlandel pr. port som tabel
    port_tab = dcc.Tab(
        label="Fejlandel pr. port",
        children=[
            dcc.Graph(
                figure=tables.build_columns_table(
                    (
                        "Port",
                        "Events",
                        "Fejl",
                        "Andel",
                        "Eksterne",
                        "Ekst. fejl",
                    ),
                    [
                        [str(row["port"]) for row in port_rows],
                        [str(row["total"]) for row in port_rows],
                        [str(row["failures"]) for row in port_rows],
                        [
                            f"{row['failure_rate'] * 100:.1f} %"
                            for row in port_rows
                        ],
                        [str(row["external"]) for row in port_rows],
                        [
                            f"{row['external_failure_rate'] * 100:.1f} %"
                            if row["external"]
                            else "-"
                            for row in port_rows
                        ],
                    ],
                )
            )
        ],
    )

    # Tallene til fane 7: de ti hyppigste brugere, kilde-IP'er og destinationer
    top_lists = analysis.top_n_lists(records)

    # Fane 7: top 10 som tre små tabeller ved siden af hinanden
    top_tab = dcc.Tab(
        label="Top 10",
        children=[
            html.Div(
                [
                    dcc.Graph(
                        figure=tables.build_top_n_table(entries, value_label)
                    )
                    for entries, value_label in (
                        (top_lists["users"], "Bruger"),
                        (top_lists["src_ips"], "Kilde-IP"),
                        (top_lists["dest_hosts"], "Destination"),
                    )
                ],
                style={
                    "display": "grid",
                    "gridTemplateColumns": TOP_N_GRID,
                    "gap": "12px",
                    "marginTop": "12px",
                },
            )
        ],
    )

    # App-objektet. layout er det der tegnes i browseren: en overskrift og en samling tabs.
    app = Dash(__name__, title="Bumle Business – logdata")
    app.layout = html.Div(
        [
            html.H2("Bumle Business – logdata"),
            dcc.Tabs(
                children=[
                    table_tab,
                    overview_tab,
                    *chart_tabs,
                    port_tab,
                    top_tab,
                ]
            ),
        ],
        style={"fontFamily": "sans-serif", "margin": "24px"},
    )

    # Callbacken kaldes automatisk, hver gang en af Input-komponenterne ændrer sig, fx når brugeren vælger et filter. Den bygger tabellen på ny og returnerer både figuren og teksten med antal rækker.
    @app.callback(
        Output("log-table", "figure"),
        Output("row-count", "children"),
        Input("event-filter", "value"),
        Input("user-filter", "value"),
        Input("level-filter", "value"),
        Input("dest_host-filter", "value"),
        Input("dest_port-filter", "value"),
        Input("status-filter", "value"),
        Input("msg-filter", "value"),
        Input("sort-column", "value"),
        Input("sort-direction", "value"),
    )
    def update_view(event, user, level, dest_host, dest_port, status, msg, column, direction):
        figure, row_count = logview.build_view(
            records, event, user, level, dest_host, dest_port, status, msg,
            column, direction == "desc",
        )
        return figure, f"{row_count} rækker"

    return app


# Starter dashboardet som en lokal webapp på den angivne port (http://127.0.0.1:8050 som standard). En optaget port giver en kort fejlbesked i stedet for et traceback.
def run(records, port=DEFAULT_PORT) -> None:
    try:
        create_app(records).run(port=port, debug=False)
    except OSError as error:
        raise DashboardError(
            f"Dashboardet kunne ikke startes på port {port}: {error}"
        ) from None
