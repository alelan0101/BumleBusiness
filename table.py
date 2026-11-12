import plotly.graph_objects as go
import plotly.io as pio

pio.renderers.default = "browser"

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


def render_table(records, columns=DEFAULT_COLUMNS) -> str:
    headers = [COLUMN_LABELS[column] for column in columns]
    rows = [[COLUMN_VALUES[column](record) for column in columns] for record in records]

    widths = []
    for index, header in enumerate(headers):
        cells = [row[index] for row in rows]
        widths.append(max([len(header), *(len(cell) for cell in cells)]))

    def format_row(values):
        cells = (value.ljust(width) for value, width in zip(values, widths))
        return "  ".join(cells).rstrip()

    lines = [format_row(headers), "  ".join("-" * width for width in widths)]
    lines.extend(format_row(row) for row in rows)
    return "\n".join(lines)


def create_table(records):
    cells = [
        [COLUMN_VALUES[column](record) for record in records] for column in DEFAULT_COLUMNS
    ]

    fig = go.Figure(
        data=[
            go.Table(
                columnwidth=[1.4, 2.5, 1.0, 0.8, 1.1, 0.8, 0.7, 0.9, 2.5],
                header={
                    "values": [COLUMN_LABELS[column] for column in DEFAULT_COLUMNS],
                    "align": "left",
                },
                cells={"values": cells, "align": "left"},
            )
        ]
    )

    fig.show()
