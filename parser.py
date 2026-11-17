"""Parsning af rå loglinjer til strukturerede logrecords."""

from datetime import datetime

from model import LogRecord


# Gør tekstlinjerne fra logfilen om til LogRecord-objekter.
# De otte første felter splitter vi ved mellemrum og deler ved "=".
# msg får vi på en anden måde, fordi beskeden kan indeholde mellemrum.
#
# Returnerer to lister: de records der kunne læses, og de linjer der blev
# sprunget over fordi de ikke passede i formatet.
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
            # Alt efter "msg=" er beskeden, også selv om den indeholder mellemrum
            msg = line.split("msg=", 1)[1]
            # Fjern de citationstegn logfilen pakker beskeden ind i
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
        # En linje med for få felter eller et ugyldigt tal stopper ikke hele
        # programmet. Den gemmes blot til sidst.
        except (IndexError, ValueError):
            skipped_lines.append(line)

    return list_of_logs, skipped_lines
