"""Filtrering og sortering af logvisningen."""

from . import tables

DEFAULT_SORT_COLUMN = "timestamp"

# Hvordan hver kolonne sorteres. Tekst sorteres med lower(), så store og små bogstaver blandes naturligt.
SORT_KEYS = {
    "timestamp": lambda record: record.timestamp,
    "event": lambda record: record.event.lower(),
    "user": lambda record: record.user.lower(),
    "level": lambda record: record.level.lower(),
    "src_ip": lambda record: record.src_ip,
    "dest_host": lambda record: record.dest_host.lower(),
    "dest_port": lambda record: record.dest_port,
    "status": lambda record: record.status.lower(),
    "msg": lambda record: record.msg.lower(),
}

# De kolonner der får et dropdown-filter i dashboardet
FILTER_ATTRIBUTES = (
    "event",
    "user",
    "level",
    "dest_host",
    "dest_port",
    "status",
)


# Returnerer kun de records hvor alle valgte filtre passer, og hvor søgeteksten findes i beskeden. Filtre der står tomme, ignoreres.
def filter_records(records, event=None, user=None, level=None, dest_host=None, dest_port=None, status=None, msg=None):
    # Saml de valgte filtre, så vi kan springe de tomme over
    selected = {
        "event": event,
        "user": user,
        "level": level,
        "dest_host": dest_host,
        "dest_port": dest_port,
        "status": status,
    }
    active = [(key, value) for key, value in selected.items() if value]

    # Søgeteksten gøres lowercase, så søgningen ikke er afhængig af store og små bogstaver
    pattern = msg.strip().lower() if msg else ""

    # all() kræver at alle filtre passer på samme tid
    return [
        record
        for record in records
        if all(str(getattr(record, key)) == value for key, value in active)
        and pattern in record.msg.lower()
    ]


# Alle forskellige værdier i en kolonne, sorteret. Tal sorteres som tal, så 80 kommer før 443 og ikke efter.
def filter_options(records, attribute) -> list[str]:
    values = {str(getattr(record, attribute)) for record in records}
    return sorted(
        values,
        key=lambda value: (0, int(value)) if value.isdigit() else (1, value),
    )


# Sorterer records efter den valgte kolonne, enten stigende eller faldende
def sort_records(records, column=DEFAULT_SORT_COLUMN, descending=False):
    if column not in SORT_KEYS:
        raise ValueError(f"Ukendt sorteringskolonne: {column}")
    return sorted(records, key=SORT_KEYS[column], reverse=descending)


# Gør hele arbejdet for logtabellen: filtrer, sorter og byg figuren.
# Returnerer figuren og antallet af rækker, så dashboardet kan vise "N rækker" over tabellen.
def build_view(records, event=None, user=None, level=None, dest_host=None, dest_port=None, status=None, msg=None, column=DEFAULT_SORT_COLUMN, descending=False):
    filtered = filter_records(
        records, event, user, level, dest_host, dest_port, status, msg
    )
    ordered = sort_records(filtered, column, descending)

    # Hvis filtrene ikke matcher noget, vises en tom tabel med en forklaring
    if ordered:
        figure = tables.build_table(ordered)
    else:
        figure = tables.build_empty_table()

    return figure, len(ordered)
