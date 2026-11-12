"""Filtrering og sortering af logvisningen."""

import table

DEFAULT_SORT_COLUMN = "timestamp"

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

FILTER_ATTRIBUTES = (
    "event",
    "user",
    "level",
    "dest_host",
    "dest_port",
    "status",
)


def filter_records(records, event=None, user=None, level=None, dest_host=None,
                   dest_port=None, status=None, msg=None):
    selected = {
        "event": event,
        "user": user,
        "level": level,
        "dest_host": dest_host,
        "dest_port": dest_port,
        "status": status,
    }
    active = [(key, value) for key, value in selected.items() if value]
    pattern = msg.strip().lower() if msg else ""
    return [
        record
        for record in records
        if all(str(getattr(record, key)) == value for key, value in active)
        and pattern in record.msg.lower()
    ]


def filter_options(records, attribute) -> list[str]:
    values = {str(getattr(record, attribute)) for record in records}
    return sorted(
        values,
        key=lambda value: (0, int(value)) if value.isdigit() else (1, value),
    )


def sort_records(records, column=DEFAULT_SORT_COLUMN, descending=False):
    if column not in SORT_KEYS:
        raise ValueError(f"Ukendt sorteringskolonne: {column}")
    return sorted(records, key=SORT_KEYS[column], reverse=descending)


def build_view(records, event=None, user=None, level=None, dest_host=None,
               dest_port=None, status=None, msg=None,
               column=DEFAULT_SORT_COLUMN, descending=False):
    filtered = filter_records(
        records, event, user, level, dest_host, dest_port, status, msg
    )
    ordered = sort_records(filtered, column, descending)

    if ordered:
        figure = table.build_table(ordered)
    else:
        figure = table.build_empty_table()

    return figure, len(ordered)
