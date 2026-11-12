from collections import defaultdict
from collections.abc import Iterable
from typing import TypedDict

from model import LogRecord


class UserIPSummary(TypedDict):
    user_count: int
    unique_ip_count: int
    ips_per_user: dict[str, int]


def get_user_ip_summary(records: Iterable[LogRecord]) -> UserIPSummary:
    users = set()
    unique_ips = set()
    ips_by_user = defaultdict(set)

    for record in records:
        users.add(record.user)
        unique_ips.add(record.src_ip)
        ips_by_user[record.user].add(record.src_ip)

    return {
        "user_count": len(users),
        "unique_ip_count": len(unique_ips),
        "ips_per_user": {
            user: len(ips) for user, ips in sorted(ips_by_user.items())
        },
    }


def format_user_ip_table(summary: UserIPSummary) -> str:
    headers = ("User", "Unique IPs")
    rows = [
        (user, str(ip_count))
        for user, ip_count in summary["ips_per_user"].items()
    ]
    widths = [
        max([len(header)] + [len(row[index]) for row in rows])
        for index, header in enumerate(headers)
    ]

    header = " | ".join(
        title.ljust(widths[index]) for index, title in enumerate(headers)
    )
    separator = "-+-".join("-" * width for width in widths)
    table_rows = [
        " | ".join(value.ljust(widths[index]) for index, value in enumerate(row))
        for row in rows
    ]
    return "\n".join((header, separator, *table_rows))


def print_user_ip_table(records: Iterable[LogRecord]) -> UserIPSummary:
    summary = get_user_ip_summary(records)
    print(format_user_ip_table(summary))
    return summary
