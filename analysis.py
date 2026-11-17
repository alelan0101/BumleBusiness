"""Statistik, aggregering og sammenhængsanalyse af logdata."""

from collections import Counter
from collections.abc import Iterable
from datetime import datetime
from typing import TypedDict

from aggregation import grouped_counts
from model import LogRecord

TOP_N = 10


class UserFailure(TypedDict):
    user: str
    failures: int
    total: int
    rate: float


class HourlySummary(TypedDict):
    average: float
    busiest_hour: int | None
    busiest_count: int
    quietest_hour: int | None
    quietest_count: int


class PortEvent(TypedDict):
    port: int
    event_category: str
    ip_scope: str
    count: int


class PortFailure(TypedDict):
    port: int
    total: int
    failures: int
    failure_rate: float
    external: int
    external_failure_rate: float


class PairSeries(TypedDict):
    time_of_day: list[tuple[int, int]]
    user_failure: list[UserFailure]
    port_event: list[PortEvent]


# Laver tre top-lister: de brugere, kilde-IP'er og dest_hosts der optræder flest gange i loggen. Dashboardets "Top 10"-fane bruger dem.
def top_n_lists( records: Iterable[LogRecord], n: int = TOP_N ) -> dict[str, list[tuple[str, int]]]:
    # highestTabel grupperer alle records, og derefter trækkes de n største ud for hver af de tre nøgler
    rows = grouped_counts.highestTabel(records=list(records))

    return {
        "users": _rank_rows(rows, "User", n),
        "src_ips": _rank_rows(rows, "src_ip", n),
        "dest_hosts": _rank_rows(rows, "dest_host", n),
    }


# Tager de n rækker med flest events for en nøgle (fx "User").
# Sorteringen er faldende på antal og alfabetisk ved samme antal,
# fordi -item[1] vender tallets rækkefølge om.
def _rank_rows(rows, key, n):
    entries = [(row[key], row["Events"]) for row in rows if key in row]

    return sorted(entries, key=lambda item: (-item[1], item[0]))[:n]


# En record tæller som fejl, hvis eventet eller statusen hører til fejl-kategorien, fx LOGIN_FAILED eller BLOCKED
def is_failure(record: LogRecord) -> bool:
    return record.event_category == "fejl" or record.status_category == "fejl"


# Finder det tidligste og det seneste tidspunkt i loggen.
# Giver (None, None), hvis der ikke er nogen records.
def time_range( records: Iterable[LogRecord], ) -> tuple[datetime | None, datetime | None]:
    timestamps = [record.timestamp for record in records]

    if not timestamps:
        return None, None

    return min(timestamps), max(timestamps)


# Tæller hvor mange records der er fejl, og hvor mange der er i alt.
# Tallene bruges til fejlraten i overbliksfanen.
def failure_counts(records: Iterable[LogRecord]) -> tuple[int, int]:
    records = list(records)
    failures = sum(1 for record in records if is_failure(record))

    return failures, len(records)


# Tæller events pr. time på dagen. Alle 24 timer kommer med, også de timer hvor der ikke skete noget, så grafen får et punkt for hver time.
def hourly_event_counts(records: Iterable[LogRecord]) -> list[tuple[int, int]]:
    counts = Counter(record.hour for record in records)

    return [(hour, counts[hour]) for hour in range(24)]


# Regner fejlraten ud pr. bruger: antal fejl divideret med antal events.
# Listen sorteres med den højeste fejlrate først.
def user_failure_rates(records: Iterable[LogRecord]) -> list[UserFailure]:
    # To Countere: en med alle events pr. bruger og en med kun fejlene
    totals = Counter()
    failures = Counter()

    for record in records:
        totals[record.user] += 1
        if is_failure(record):
            failures[record.user] += 1

    rates: list[UserFailure] = [
        {
            "user": user,
            "failures": failures[user],
            "total": total,
            "rate": failures[user] / total,
        }
        for user, total in totals.items()
    ]

    return sorted(rates, key=lambda entry: (-entry["rate"], entry["user"]))


# Tæller events for hver kombination af destinationsport, event-kategori (succes/fejl/neutral) og IP-klasse. Hver kombination bliver en boble i port-diagrammet.
def port_event_series(records: Iterable[LogRecord]) -> list[PortEvent]:
    counts = Counter(
        (record.dest_port, record.event_category, record.ip_scope)
        for record in records
    )
    series: list[PortEvent] = [
        {
            "port": port,
            "event_category": category,
            "ip_scope": scope,
            "count": count,
        }
        for (port, category, scope), count in counts.items()
    ]
    return sorted(
        series,
        key=lambda entry: (
            entry["port"],
            entry["event_category"],
            entry["ip_scope"],
        ),
    )


# Opsummerer døgnet: gennemsnit pr. time, den travleste time og den time med færrest events. Bruges som tekst over diagrammet.
def hourly_summary(records: Iterable[LogRecord]) -> HourlySummary:
    hourly = hourly_event_counts(records)

    # Hvis alle 24 timer har nul events, er der intet at opsummere
    if not any(count for _, count in hourly):
        return {
            "average": 0.0,
            "busiest_hour": None,
            "busiest_count": 0,
            "quietest_hour": None,
            "quietest_count": 0,
        }

    # max() og min() ser på antallet (item[1]) og giver hele (time, antal)-parret
    busiest_hour, busiest_count = max(hourly, key=lambda item: item[1])
    quietest_hour, quietest_count = min(hourly, key=lambda item: item[1])
    total = sum(count for _, count in hourly)

    return {
        "average": total / len(hourly),
        "busiest_hour": busiest_hour,
        "busiest_count": busiest_count,
        "quietest_hour": quietest_hour,
        "quietest_count": quietest_count,
    }


# Laver en række pr. port med totaler, fejl, fejlrate og det samme for eksterne IP'er. Rækkerne bruges i tabellen "Fejlandel pr. port".
def port_failure_rows(records: Iterable[LogRecord]) -> list[PortFailure]:
    # Fire Countere, så vi kan se forskel på alle events og kun de eksterne
    totals = Counter()
    external = Counter()
    failures = Counter()
    external_failures = Counter()

    for record in records:
        port = record.dest_port
        totals[port] += 1
        failures[port] += is_failure(record)
        if record.ip_scope == "ekstern":
            external[port] += 1
            external_failures[port] += is_failure(record)

    # Byg rækkerne i portnummerets rækkefølge, så tabellen bliver let at læse
    return [
        {
            "port": port,
            "total": totals[port],
            "failures": failures[port],
            "failure_rate": failures[port] / totals[port],
            "external": external[port],
            "external_failure_rate": (
                external_failures[port] / external[port]
                if external[port]
                else 0.0
            ),
        }
        for port in sorted(totals)
    ]
