"""Unikke brugere og kilde-IP'er pr. bruger."""

from collections import defaultdict
from collections.abc import Iterable
from typing import TypedDict

from model import LogRecord


class UserIPSummary(TypedDict):
    user_count: int
    unique_ip_count: int
    ips_per_user: dict[str, int]


# Opsummerer hvor mange brugere og IP-adresser loggen indeholder, og hvor mange forskellige IP'er hver bruger har brugt.
def get_user_ip_summary(records: Iterable[LogRecord]) -> UserIPSummary:
    # Set bruges, fordi hver bruger og IP kun skal tælles en gang, uanset hvor mange gange den optræder i loggen
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


# Bygger en teksttabel med to kolonner: header, en streg under og en række pr. bruger.
# Kolonnebredden sættes efter den længste tekst i kolonnen.
def format_user_ip_table(summary: UserIPSummary) -> str:
    headers = ("User", "Unique IPs")
    rows = [
        (user, str(ip_count))
        for user, ip_count in summary["ips_per_user"].items()
    ]
    # Bredden på hver kolonne er længden af den længste tekst, header medregnet
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


# Henter opsummeringen, printer den som tabel og returnerer tallene (så de fx kan bruges igen af den der kaldte funktionen)
def print_user_ip_table(records: Iterable[LogRecord]) -> UserIPSummary:
    summary = get_user_ip_summary(records)
    print(format_user_ip_table(summary))
    return summary
