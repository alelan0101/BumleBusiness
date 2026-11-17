"""Gruppering og optælling af events pr. bruger, IP, vært og port."""

from collections import Counter, defaultdict
from collections.abc import Callable


# Bygger de grupperede rækker som konsoltabellerne og top-10-listerne bruger.
# For hver bruger, kilde-IP, destinationsvært og port tælles det, hvor mange events der er, og hvordan de fordeler sig på event, level og status.
# AllData sendes med fra counts.filtering, men bruges ikke her. Alle tal udregnes ud fra records.
def highestTabel(AllData=None, records=()):
    # Fire dictionaries der hver mapper en værdi (fx en bruger) til en Counter med antal pr. event, level og status
    counts_by_user = defaultdict(Counter)
    counts_by_ip = defaultdict(Counter)
    counts_by_host = defaultdict(Counter)
    counts_by_port = defaultdict(Counter)
    service_by_port = {}

    for record in records:
        # Husk hvilken service porten hører til, så tabellen kan vise "443 (HTTPS)" i stedet for bare 443
        service_by_port.setdefault(record.dest_port, record.service)

        # De samme optællinger opdateres for alle fire grupperinger på en gang
        counters = (
            counts_by_user[record.user],
            counts_by_ip[record.src_ip],
            counts_by_host[record.dest_host],
            counts_by_port[record.dest_port],
        )
        # "Events", "Level" og "Status" bliver alle sammen totaler for gruppen.
        # De andre nøgler (fx "LOGIN_FAILED" eller "WARN") er antal pr. værdi.
        for counts in counters:
            counts["Events"] += 1
            counts["Level"] += 1
            counts["Status"] += 1
            counts[record.event] += 1
            counts[record.level] += 1
            counts[record.status] += 1

    # Rækkerne lægges i en lang liste: først pr. bruger, så pr. IP, pr. vært og til sidst pr. port
    compiled_data = _group_rows(counts_by_user, "User")
    compiled_data.extend(_group_rows(counts_by_ip, "src_ip"))
    compiled_data.extend(_group_rows(counts_by_host, "dest_host"))

    # Port-rækkerne får teksten "443 (HTTPS)" i stedet for bare tallet 443
    compiled_data.extend(
        _group_rows(
            counts_by_port,
            "dest",
            lambda port: f"{port} ({service_by_port[port]})",
        )
    )

    return compiled_data


# Laver en dictionary pr. gruppe, fx {"User": "anna", "Events": 42, ...}.
# Rækkerne sorteres efter nøglen, så rækkefølgen er den samme hver gang.
def _group_rows( counts_by_value, key: str, format_value: Callable[[object], str] = str):
    return [
        {key: format_value(value), **counts_by_value[value]}
        for value in sorted(counts_by_value)
    ]
