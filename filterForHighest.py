from collections import Counter, defaultdict


def highestTabel(AllData, records):
    counts_by_user = defaultdict(Counter)
    counts_by_port = defaultdict(Counter)
    service_by_port = {}

    for record in records:
        service_by_port.setdefault(record.dest_port, record.service)
        for counts in (counts_by_user[record.user], counts_by_port[record.dest_port]):
            counts["Events"] += 1
            counts["Level"] += 1
            counts["Status"] += 1
            counts[record.event] += 1
            counts[record.level] += 1
            counts[record.status] += 1

    compiled_data = [
        {"User": user, **counts_by_user[user]}
        for user in sorted(counts_by_user)
    ]
    compiled_data.extend(
        {
            "dest": f"{port} ({service_by_port[port]})",
            **counts_by_port[port],
        }
        for port in sorted(counts_by_port)
    )
    return compiled_data
