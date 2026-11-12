""" Byg Plotly table """

import plotly.graph_objects as go

from config import COLUMN_WIDTHS

ELLIPSIS = "…"
MSG_LIMIT = 40
NEUTRAL_CELL_COLOR = "#ffffff"
NO_RESULTS_MESSAGE = "Ingen resultater matcher filtrene"

ROW_HEIGHT = 30
HEADER_HEIGHT = 30
EMPTY_TABLE_HEIGHT = 200
MARGIN = {"l": 20, "r": 20, "t": 20, "b": 20}

COLUMN_LABELS = {
    "timestamp": "Tid",
    "event": "Event",
    "user": "Bruger",
    "level": "Level",
    "src_ip": "Kilde-IP",
    "dest_host": "Destination",
    "dest_port": "Port",
    "status": "Status",
    "msg": "Besked",
}

COLUMN_VALUES = {
    "timestamp": lambda record: record.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
    "event": lambda record: str(record.event),
    "user": lambda record: str(record.user),
    "level": lambda record: str(record.level),
    "src_ip": lambda record: str(record.src_ip),
    "dest_host": lambda record: str(record.dest_host),
    "dest_port": lambda record: str(record.dest_port),
    "status": lambda record: str(record.status),
    "msg": lambda record: str(record.msg),
}

DEFAULT_COLUMNS = tuple(COLUMN_LABELS)

COLORED_COLUMNS = ("level", "status")

CELL_COLORS = {
    "INFO": "#c8e6c9",
    "WARN": "#ffe0b2",
    "ALERT": "#ffcdd2",
    "OK": "#c8e6c9",
    "FAILED": "#ffcdd2",
    "BLOCKED": "#ffcdd2",
}


def format_cell(record, column) -> str:
    value = COLUMN_VALUES[column](record)
    if column == "msg" and len(value) > MSG_LIMIT:
        return value[:MSG_LIMIT] + ELLIPSIS
    return value


def cell_fill(records, column):
    if column not in COLORED_COLUMNS:
        return NEUTRAL_CELL_COLOR
    return [
        CELL_COLORS.get(format_cell(record, column), NEUTRAL_CELL_COLOR)
        for record in records
    ]


def build_table(records, columns=DEFAULT_COLUMNS):
    cells = [
        [format_cell(record, column) for record in records]
        for column in columns
    ]
    fills = [cell_fill(records, column) for column in columns]

    figure = go.Figure(
        data=[
            go.Table(
                columnwidth=[COLUMN_WIDTHS[column] for column in columns],
                header={
                    "values": [COLUMN_LABELS[column] for column in columns],
                    "align": "left",
                    "fill": {"color": "#e0e0e0"},
                },
                cells={
                    "values": cells,
                    "align": "left",
                    "fill": {"color": fills},
                },
            )
        ]
    )
    height = HEADER_HEIGHT + ROW_HEIGHT * len(records)
    height += MARGIN["t"] + MARGIN["b"]
    figure.update_layout(margin=MARGIN, height=height)
    return figure


def build_empty_table(columns=DEFAULT_COLUMNS):
    figure = build_table([], columns)
    figure.add_annotation(
        text=NO_RESULTS_MESSAGE,
        showarrow=False,
        font={"size": 16},
    )
    figure.update_layout(height=EMPTY_TABLE_HEIGHT)
    return figure
