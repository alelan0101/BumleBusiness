"""Datamodel for strukturerede logrecords."""

from dataclasses import dataclass, field
from datetime import datetime

WEEKDAYS = (
    "mandag",
    "tirsdag",
    "onsdag",
    "torsdag",
    "fredag",
    "lørdag",
    "søndag",
)

PORT_SERVICES = {
    22: "SSH",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    443: "HTTPS",
    445: "SMB",
    3389: "RDP",
    8080: "HTTP-ALT",
}

SUCCESS_EVENTS = {"LOGIN_SUCCESS"}
FAILED_EVENTS = {"LOGIN_FAILED"}
SUCCESS_STATUSES = {"OK"}
FAILED_STATUSES = {"FAILED", "BLOCKED"}


def classify_ip(address: str) -> str:
    octets = address.split(".")
    if len(octets) != 4 or not all(octet.isdigit() for octet in octets):
        return "ekstern"

    first, second = int(octets[0]), int(octets[1])
    if first == 10:
        return "intern"
    if first == 172 and 16 <= second <= 31:
        return "intern"
    if first == 192 and second == 168:
        return "intern"
    return "ekstern"


def service_name(port: int) -> str:
    return PORT_SERVICES.get(port, "Ukendt")


def categorize_event(event: str) -> str:
    if event in SUCCESS_EVENTS:
        return "succes"
    if event in FAILED_EVENTS:
        return "fejl"
    return "neutral"


def categorize_status(status: str) -> str:
    if status in SUCCESS_STATUSES:
        return "succes"
    if status in FAILED_STATUSES:
        return "fejl"
    return "neutral"


@dataclass
class LogRecord:
    timestamp: datetime
    level: str
    event: str
    user: str
    src_ip: str
    dest_host: str
    dest_port: int
    status: str
    msg: str
    hour: int = field(init=False)
    weekday: str = field(init=False)
    date: str = field(init=False)
    ip_scope: str = field(init=False)
    service: str = field(init=False)
    event_category: str = field(init=False)
    status_category: str = field(init=False)

    def __post_init__(self):
        self.hour = self.timestamp.hour
        self.weekday = WEEKDAYS[self.timestamp.weekday()]
        self.date = self.timestamp.date().isoformat()
        self.ip_scope = classify_ip(self.src_ip)
        self.service = service_name(self.dest_port)
        self.event_category = categorize_event(self.event)
        self.status_category = categorize_status(self.status)
