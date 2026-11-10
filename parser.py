"""Parsning af rå loglinjer til strukturerede logrecords."""


from datetime import datetime

from model import LogRecord


def log_line_parser(lines) -> tuple[list[LogRecord], list[str]]:
    list_of_logs = []
    skipped_lines = []
    for line in lines:
        try:
            (
                timestamp,
                level,
                event,
                user,
                src_ip,
                dest_host,
                dest_port,
                status,
                *_,
            ) = line.split(" ")
            msg = line.split("msg=", 1)[1]
            if msg.startswith('"') and msg.endswith('"'):
                msg = msg[1:-1]
            list_of_logs.append(
                LogRecord(
                    timestamp=datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S"),
                    level=level.split("=")[1],
                    event=event.split("=")[1],
                    user=user.split("=")[1],
                    src_ip=src_ip.split("=")[1],
                    dest_host=dest_host.split("=")[1],
                    dest_port=int(dest_port.split("=")[1]),
                    status=status.split("=")[1],
                    msg=msg,
                )
            )
        except (IndexError, ValueError):
            skipped_lines.append(line)
    return list_of_logs, skipped_lines
