"""Scatter-plots til sammenhængsanalysen af logdata."""

import plotly.graph_objects as go

import analysis
from model import service_name

# Farver og labels bruges i diagrammerne, så intern/ekstern og succes/fejl/neutral kan kendes igen på tværs af plots
SCOPE_COLORS = {
    "intern": "#2e7d32",
    "ekstern": "#c62828",
    "invalid": "#616161",
}
CATEGORY_LABELS = {"succes": "Succes", "neutral": "Neutral", "fejl": "Fejl"}
CATEGORY_ORDER = ("succes", "neutral", "fejl")
NO_DATA_MESSAGE = "Ingen data at vise"

# Fælles layout for alle tre diagrammer: hvid baggrund, samme font og samme højde, så fanerne ligner hinanden
BASE_LAYOUT = {
    "template": "plotly_white",
    "font": {"family": "sans-serif", "size": 13},
    "margin": {"l": 70, "r": 30, "t": 60, "b": 90},
    "height": 500,
}


# Sætter titel, akser og den fælles stil på en figur og returnerer figuren **overrides bruges til de indstillinger der kun gælder for et diagram
def _layout(figure, title, x_axis, y_axis, **overrides):
    figure.update_layout(
        title=title,
        xaxis=x_axis,
        yaxis=y_axis,
        **BASE_LAYOUT,
        **overrides,
    )
    return figure


# Tom figur med en tekst midt i, brugt når der ikke er data at vise
def _empty_figure(title, x_title, y_title):
    figure = go.Figure()
    figure.add_annotation(
        text=NO_DATA_MESSAGE, showarrow=False, font={"size": 16}
    )
    return _layout(figure, title, {"title": x_title}, {"title": y_title})


# Punktdiagram med et punkt pr. time på dagen. x er timen (0-23), og y er antal events i den time.
def hour_event_scatter(records):
    title = "Events pr. time på dagen"
    if not records:
        return _empty_figure(title, "Time på dagen", "Antal events")

    series = analysis.hourly_event_counts(records)
    figure = go.Figure(
        go.Scatter(
            x=[hour for hour, _ in series],
            y=[count for _, count in series],
            mode="markers",
            marker={"size": 10, "color": "#1565c0"},
            hovertemplate="Kl. %{x}: %{y} events<extra></extra>",
            name="Events",
        )
    )
    return _layout(
        figure,
        title,
        {
            "title": "Time på dagen",
            "tick0": 0,
            "dtick": 1,
            "range": [-0.5, 23.5],
        },
        {"title": "Antal events", "rangemode": "tozero"},
        showlegend=False,
    )


# Punktdiagram med et punkt pr. bruger. y er hvor stor en del af brugerens events der var fejl, og den stiplede linje er gennemsnittet for alle.
def user_failure_scatter(records):
    title = "Andel fejl pr. bruger"
    if not records:
        return _empty_figure(title, "Bruger", "Andel fejl (%)")

    # Den samlede fejlrate udregnes for at kunne tegne referencelinjen
    series = analysis.user_failure_rates(records)
    total_failures = sum(entry["failures"] for entry in series)
    total_events = sum(entry["total"] for entry in series)
    overall_rate = total_failures / total_events * 100 if total_events else 0

    figure = go.Figure(
        go.Scatter(
            x=[entry["user"] for entry in series],
            y=[entry["rate"] * 100 for entry in series],
            mode="markers",
            marker={"size": 12, "color": "#6a1b9a"},
            customdata=[
                [entry["failures"], entry["total"]] for entry in series
            ],
            hovertemplate=(
                "%{x}: %{y:.1f} % fejl "
                "(%{customdata[0]} af %{customdata[1]} events)"
                "<extra></extra>"
            ),
            name="Brugere",
        )
    )
    figure.add_hline(
        y=overall_rate,
        line={"dash": "dash", "color": "#616161"},
        annotation_text=f"Samlet fejlrate: {overall_rate:.1f} %",
        annotation_position="top left",
    )
    return _layout(
        figure,
        title,
        {"title": "Bruger", "type": "category"},
        {"title": "Andel fejl (%)", "rangemode": "tozero"},
        showlegend=False,
    )


# Boblediagram: port på x-aksen og eventtype på y-aksen. Boblens størrelse er antal events, og farven viser om IP'en er intern eller ekstern. Fire variable i samme plot.
def port_event_scatter(records):
    title = "Destinationsport vs. eventtype og IP-klasse"
    if not records:
        return _empty_figure(title, "Destinationsport", "Eventtype")

    series = analysis.port_event_series(records)
    ports = sorted({entry["port"] for entry in series})
    labels = [f"{port} ({service_name(port)})" for port in ports]
    label_by_port = dict(zip(ports, labels))
    max_count = max(entry["count"] for entry in series)

    # En trace pr. IP-klasse, så de får hver sin farve i legend'en
    figure = go.Figure()
    for scope in sorted({entry["ip_scope"] for entry in series}):
        entries = [entry for entry in series if entry["ip_scope"] == scope]
        figure.add_trace(
            go.Scatter(
                x=[label_by_port[entry["port"]] for entry in entries],
                y=[
                    CATEGORY_LABELS[entry["event_category"]]
                    for entry in entries
                ],
                mode="markers",
                marker={
                    "size": [entry["count"] for entry in entries],
                    "sizemode": "area",
                    "sizeref": 2 * max_count / 40**2,
                    "sizemin": 4,
                    "color": SCOPE_COLORS.get(scope, "#616161"),
                    "opacity": 0.75,
                },
                customdata=[
                    [entry["count"], entry["ip_scope"]] for entry in entries
                ],
                hovertemplate=(
                    "%{x} – %{y}<br>%{customdata[0]} events "
                    "(%{customdata[1]} IP)<extra></extra>"
                ),
                name=scope,
            )
        )

    return _layout(
        figure,
        title,
        {
            "title": "Destinationsport",
            "type": "category",
            "categoryorder": "array",
            "categoryarray": labels,
        },
        {
            "title": "Eventtype",
            "type": "category",
            "categoryorder": "array",
            "categoryarray": [
                CATEGORY_LABELS[category] for category in CATEGORY_ORDER
            ],
        },
        legend={"title": {"text": "IP-klasse"}},
    )


# Bygger alle tre diagrammer og returnerer dem i en dictionary med faste nøgler, som dashboardet slår op i
def build_figures(records) -> dict[str, go.Figure]:
    records = list(records)
    return {
        "events_by_hour": hour_event_scatter(records),
        "user_failure_rate": user_failure_scatter(records),
        "port_event": port_event_scatter(records),
    }
