"""Plotly-tabeller til logdata, top-10 og fejlandel pr. port."""

import plotly.graph_objects as go

from config import COLUMN_WIDTHS

ELLIPSIS = "…"
MSG_LIMIT = 40
NEUTRAL_CELL_COLOR = "#ffffff"
HEADER_FILL = "#e0e0e0"
NO_RESULTS_MESSAGE = "Ingen resultater matcher filtrene"

ROW_HEIGHT = 30
HEADER_HEIGHT = 30
EMPTY_TABLE_HEIGHT = 200
MARGIN = {"l": 20, "r": 20, "t": 20, "b": 20}

# De tekstnavne der vises i tabellens header i stedet for feltnavnene
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

# Hvordan et felt hentes ud af en record og laves om til tekst i tabellen
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

# Kun disse to kolonner får farvet baggrund, så de skiller sig ud
COLORED_COLUMNS = ("level", "status")

# Farve pr. værdi: grøn for det der gik godt, rød/orange for det der kræver opmærksomhed
CELL_COLORS = {
    "INFO": "#c8e6c9",
    "WARN": "#ffe0b2",
    "ALERT": "#ffcdd2",
    "OK": "#c8e6c9",
    "FAILED": "#ffcdd2",
    "BLOCKED": "#ffcdd2",
}


# Henter teksten til en celle. Lange beskeder klippes af, så rækken ikke bliver meget bred.
def format_cell(record, column) -> str:
    value = COLUMN_VALUES[column](record)
    if column == "msg" and len(value) > MSG_LIMIT:
        return value[:MSG_LIMIT] + ELLIPSIS
    return value


# Returnerer baggrundsfarven for hver celle i en kolonne. Enten en farve til hele kolonnen eller en liste med en farve pr. række.
def cell_fill(records, column):
    if column not in COLORED_COLUMNS:
        return NEUTRAL_CELL_COLOR
    return [
        CELL_COLORS.get(format_cell(record, column), NEUTRAL_CELL_COLOR)
        for record in records
    ]


# Bygger logtabellen: en kolonne pr. felt og en række pr. record.
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
                    "fill": {"color": HEADER_FILL},
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


# Bygger en tabel ud fra færdige kolonner, dvs. når tallene allerede er regnet ud. Bruges til top-10, overblikket og port-tabellen.
def build_columns_table(headers, columns):
    figure = go.Figure(
        data=[
            go.Table(
                header={
                    "values": list(headers),
                    "align": "left",
                    "fill": {"color": HEADER_FILL},
                },
                cells={"values": columns, "align": "left"},
            )
        ]
    )
    rows = max((len(column) for column in columns), default=0)
    height = HEADER_HEIGHT + ROW_HEIGHT * max(rows, 1)
    height += MARGIN["t"] + MARGIN["b"]
    figure.update_layout(margin=MARGIN, height=height)
    return figure


# Tabel med to kolonner: værdien (fx et brugernavn) og antal events
def build_top_n_table(entries, value_label, count_label="Events"):
    return build_columns_table(
        (value_label, count_label),
        (
            [value for value, _ in entries],
            [count for _, count in entries],
        ),
    )


# Tabel uden rækker og med en tekst om at filtrene ikke matcher noget
def build_empty_table(columns=DEFAULT_COLUMNS):
    figure = build_table([], columns)
    figure.add_annotation(
        text=NO_RESULTS_MESSAGE,
        showarrow=False,
        font={"size": 16},
    )
    figure.update_layout(height=EMPTY_TABLE_HEIGHT)
    return figure
