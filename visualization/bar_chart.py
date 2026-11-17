"""Søjlediagram med antal events pr. eventtype, bygget på de indlæste records."""

from collections import Counter

import plotly.graph_objects as go

from .scatter_plots import BASE_LAYOUT, NO_DATA_MESSAGE

TITLE = "Hændelser pr. eventtype"


# Tom figur med en tekst midt i, brugt når der ikke er records at tælle
def _empty_figure() -> go.Figure:
    figure = go.Figure()
    figure.add_annotation(
        text=NO_DATA_MESSAGE, showarrow=False, font={"size": 16}
    )
    figure.update_layout(
        title=TITLE,
        xaxis={"title": "Eventtype"},
        yaxis={"title": "Antal hændelser"},
        **BASE_LAYOUT,
    )
    return figure


# Tæller events pr. eventtype i de indlæste records og tegner dem som søjler, flest først
def event_bar_chart(records) -> go.Figure:
    counts = Counter(record.event for record in records)

    if not counts:
        return _empty_figure()

    events = sorted(counts, key=lambda event: (-counts[event], event))
    values = [counts[event] for event in events]

    figure = go.Figure(
        go.Bar(
            x=events,
            y=values,
            marker_color="#1565c0",
            text=values,
            textposition="outside",
            hovertemplate="%{x}: %{y} events<extra></extra>",
            name="Events",
        )
    )
    figure.update_layout(
        title=TITLE,
        xaxis={"title": "Eventtype", "tickangle": -45},
        yaxis={"title": "Antal hændelser", "rangemode": "tozero"},
        **BASE_LAYOUT,
        showlegend=False,
    )
    return figure
