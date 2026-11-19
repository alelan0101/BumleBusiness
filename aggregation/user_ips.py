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

    # Samme som dette, måske lettere at læse:
#     ips_per_user = {}
#     for user, ips in sorted(ips_by_user.items()):
#         ips_per_user[user] = len(ips)
#     return {
#         "user_count": len(users),
#         "unique_ip_count": len(unique_ips),
#         "ips_per_user": ips_per_user,
#     }


# Bygger en teksttabel med to kolonner: header, en streg under og en række pr. bruger.
# Kolonnebredden sættes efter den længste tekst i kolonnen.
def format_user_ip_table(summary: UserIPSummary) -> str:
    headers = ("User", "Unique IPs")
    rows = [
        (user, str(ip_count))
        for user, ip_count in summary["ips_per_user"].items()
    ]

    # Samme som dette, måske lettere at læse:
#     rows = []
#     for user, ip_count in summary["ips_per_user"].items():
#         rows.append((user, str(ip_count)))

    # Bredden på hver kolonne er længden af den længste tekst, header medregnet
    widths = [
        max([len(header)] + [len(row[index]) for row in rows])
        for index, header in enumerate(headers)
    ]

    # Samme som dette, måske lettere at læse:
#     widths = []
#     for index, header in enumerate(headers):
#         lengths = [len(header)]
#         for row in rows:
#             lengths.append(len(row[index]))
#         widths.append(max(lengths))

    header = " | ".join(
        title.ljust(widths[index]) for index, title in enumerate(headers)
    )

    # Samme som dette, måske lettere at læse:
#     parts = []
#     for index, title in enumerate(headers):
#         parts.append(title.ljust(widths[index]))
#     header = " | ".join(parts)

    separator = "-+-".join("-" * width for width in widths)

    # Samme som dette, måske lettere at læse:
#     parts = []
#     for width in widths:
#         parts.append("-" * width)
#     separator = "-+-".join(parts)

    table_rows = [
        " | ".join(value.ljust(widths[index]) for index, value in enumerate(row))
        for row in rows
    ]

    # Samme som dette, måske lettere at læse:
#     table_rows = []
#     for row in rows:
#         parts = []
#         for index, value in enumerate(row):
#             parts.append(value.ljust(widths[index]))
#         table_rows.append(" | ".join(parts))
    return "\n".join((header, separator, *table_rows))


# Henter opsummeringen, printer den som tabel og returnerer tallene (så de fx kan bruges igen af den der kaldte funktionen)
def print_user_ip_table(records: Iterable[LogRecord]) -> UserIPSummary:
    summary = get_user_ip_summary(records)
    print(format_user_ip_table(summary))
    return summary
