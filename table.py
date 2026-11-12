import plotly.graph_objects as go
import plotly.io as pio

pio.renderers.default = "browser"


def create_table(records):
    columns = [
        "time",
        "event",
        "who",
        "level",
        "src",
        "dest",
        "port",
        "status",
        "msg",
    ]

    cells = [
        [record.timestamp.strftime("%Y-%m-%d %H:%M:%S") for record in records],
        [record.event for record in records],
        [record.user for record in records],
        [record.level for record in records],
        [record.src_ip for record in records],
        [record.dest_host for record in records],
        [record.dest_port for record in records],
        [record.status for record in records],
        [record.msg for record in records],
    ]

    fig = go.Figure(
        data=[
            go.Table(
                columnwidth=[1.4, 2.5, 1.0, 0.8, 1.1, 0.8, 0.7, 0.9, 2.5],
                header=dict(values=columns, align="left"),
                cells=dict(values=cells, align="left"),
            )
        ]
    )

    fig.show()