"""Regelbaseret detektion af mistænkelige konti."""

from collections import Counter, defaultdict
from collections.abc import Iterable, Mapping

from config import SUS_DETECTION
from model import LogRecord


# Gennemgår loggen og finder brugere der gentagne gange gør noget mistænkeligt indefra netværket.
# For hver bruger tælles de events der står i reglerne (fx ALERT og MALWARE_SIGNATURE_MATCH).
# Når tærsklen er nået, beskrives det hvor det først skete, og hvad samme IP gjorde bagefter.
# Returnerer en tekst med et afsnit pr. mistænkelig bruger.
def track_suspicious_accounts( records: Iterable[LogRecord], rules: Mapping[str, int] | None = None) -> str:
    detection_rules = SUS_DETECTION if rules is None else rules
    _validate_rules(detection_rules)

    # Sorter efter tid, så "første gang" og "næste gang" giver mening
    ordered_records = sorted(records, key=lambda record: record.timestamp)

    # Tæl kun events fra interne IP'er, og kun de events reglerne nævner.
    # Counteren pr. bruger slås op som [bruger][event]
    internal_event_counts: dict[str, Counter[str]] = defaultdict(Counter)
    for record in ordered_records:
        if record.ip_scope == "intern" and record.event in detection_rules:
            internal_event_counts[record.user][record.event] += 1

    traces = []
    for user in sorted(internal_event_counts):
        # Hvilke regler har denne bruger brudt? Eventet skal nå tærsklen.
        triggered_rules = {
            event: internal_event_counts[user][event]
            for event, threshold in detection_rules.items()
            if internal_event_counts[user][event] >= threshold
        }
        if not triggered_rules:
            continue

        # Find den første event fra brugeren som brød en regel
        entry_index = next(
            index
            for index, record in enumerate(ordered_records)
            if record.user == user
            and record.ip_scope == "intern"
            and record.event in triggered_rules
        )
        entry = ordered_records[entry_index]

        # Find næste sted samme IP dukkede op, men på en anden vært eller port.
        # Hvis der ikke er nogen, bliver next_record None.
        next_record = next(
            (
                record
                for record in ordered_records[entry_index + 1 :]
                if record.src_ip == entry.src_ip
                and (record.dest_host, record.dest_port)
                != (entry.dest_host, entry.dest_port)
            ),
            None,
        )
        # Teksten viser hvad der skete, hvilken IP der var involveret, og hvor IP'en gik hen bagefter
        entry_location = f"{entry.event} at {entry.dest_host}:{entry.dest_port}"
        next_location = (
            f"{next_record.event} at {next_record.dest_host}:{next_record.dest_port}"
            if next_record is not None
            else "no later place"
        )
        traces.append(f"{entry_location} -> {entry.src_ip} -> {next_location}")

    return "\n\n".join(traces) if traces else "No suspicious accounts found."


# Tjekker at reglerne i config.py er sat rigtigt op, så en tastefejl giver en klar fejlbesked i stedet for et forvirrende crash senere
def _validate_rules(rules: Mapping[str, int]) -> None:
    for event, threshold in rules.items():
        if not isinstance(event, str) or not event:
            raise ValueError("Detection rule event names must be non-empty strings.")
        if isinstance(threshold, bool) or not isinstance(threshold, int) or threshold < 1:
            raise ValueError(
                f"Detection threshold for {event!r} must be a positive integer."
            )
