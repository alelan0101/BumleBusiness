"""Dash-visning af logdata i en interaktiv tabel."""

from dash import Dash, Input, Output, dcc, html

import logview
import table

DEFAULT_PORT = 8050

FILTER_GRID = "repeat(auto-fit, minmax(120px, 1fr))"


def create_app(records) -> Dash:
    columns = list(table.DEFAULT_COLUMNS)

    filter_dropdowns = [
        html.Div(
            [
                html.Label(table.COLUMN_LABELS[attribute]),
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

    msg_filter = html.Div(
        [
            html.Label(table.COLUMN_LABELS["msg"]),
            dcc.Input(
                id="msg-filter",
                type="text",
                placeholder="Søg i besked",
                debounce=True,
            ),
        ]
    )

    sort_controls = [
        html.Div(
            [
                html.Label("Sorter efter"),
                dcc.Dropdown(
                    id="sort-column",
                    options=[
                        {"label": table.COLUMN_LABELS[column], "value": column}
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

    figure = logview.build_view(records)[0]

    app = Dash(__name__, title="Bumle Business – logtabel")
    app.layout = html.Div(
        [
            html.H2("Logtabel"),
            html.Div(
                filter_dropdowns + [msg_filter] + sort_controls,
                style={
                    "display": "grid",
                    "gridTemplateColumns": FILTER_GRID,
                    "gap": "12px",
                },
            ),
            html.Div(html.Span(id="row-count"), style={"margin": "16px 0"}),
            dcc.Graph(id="log-table", figure=figure),
        ],
        style={"fontFamily": "sans-serif", "margin": "24px"},
    )

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
    def update_view(event, user, level, dest_host, dest_port, status, msg,
                    column, direction):
        figure, row_count = logview.build_view(
            records, event, user, level, dest_host, dest_port, status, msg,
            column, direction == "desc",
        )
        return figure, f"{row_count} rækker"

    return app


def run(records, port=DEFAULT_PORT) -> None:
    create_app(records).run(port=port, debug=False)
