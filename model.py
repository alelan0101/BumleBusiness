"""Datamodel for strukturerede logrecords."""

from dataclasses import dataclass, field
from datetime import datetime

# Python nummererer ugedage fra 0 (mandag) til 6 (søndag), så denne liste oversætter tallet til et dansk navn
WEEKDAYS = (
    "mandag",
    "tirsdag",
    "onsdag",
    "torsdag",
    "fredag",
    "lørdag",
    "søndag",
)

# Kendte portnumre oversat til servicenavne, så tabellerne kan vise "HTTPS" i stedet for bare 443
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

# De event- og status-værdier der betyder succes eller fejl. Alt andet regnes som neutralt.
SUCCESS_EVENTS = {"LOGIN_SUCCESS"}
FAILED_EVENTS = {"LOGIN_FAILED"}
SUCCESS_STATUSES = {"OK"}
FAILED_STATUSES = {"FAILED", "BLOCKED"}


# Afgør om en IP-adresse hører til det lokale netværk eller kommer udefra.
# Adressen deles ved punktummer, så de fire tal kan undersøges hver for sig.
def classify_ip(address: str) -> str:
    octets = address.split(".")

    # En rigtig IPv4-adresse har præcis fire tal, hver mellem 0 og 255
    if len(octets) != 4:
        return "invalid"
    # Samme som dette, måske lettere at læse:
    # invalid = False
    # for octet in octets:
    #     if not (octet.isdigit() and 0 <= int(octet) <= 255):
    #         invalid = True
    # if invalid:
    #     return "invalid"
    if not all(octet.isdigit() and 0 <= int(octet) <= 255 for octet in octets):
        return "invalid"

    first, second = int(octets[0]), int(octets[1])

    # De tre private intervaler: 10.x.x.x, 172.16-31.x.x og 192.168.x.x
    if first == 10:
        return "intern"
    if first == 172 and 16 <= second <= 31:
        return "intern"
    if first == 192 and second == 168:
        return "intern"

    # Alt andet er en adresse på internettet
    return "ekstern"


# Slår portnummeret op i PORT_SERVICES og giver "Ukendt", hvis porten ikke står i listen
def service_name(port: int) -> str:
    return PORT_SERVICES.get(port, "Ukendt")


# Oversætter et event-navn til en grov kategori. Analyserne behøver så kun at kende "succes", "fejl" og "neutral" i stedet for alle event-navne.
def categorize_event(event: str) -> str:
    if event in SUCCESS_EVENTS:
        return "succes"
    if event in FAILED_EVENTS:
        return "fejl"
    return "neutral"


# Samme ide som categorize_event, men for status-kolonnen (OK, FAILED, BLOCKED)
def categorize_status(status: str) -> str:
    if status in SUCCESS_STATUSES:
        return "succes"
    if status in FAILED_STATUSES:
        return "fejl"
    return "neutral"


# Et datapunkt fra logfilen, dvs. en loglinje der er parset færdig.
@dataclass
class LogRecord:
    # Felterne herunder kommer direkte fra loglinjen
    timestamp: datetime
    level: str
    event: str
    user: str
    src_ip: str
    dest_host: str
    dest_port: int
    status: str
    msg: str

    # Felterne herunder står ikke i loglinjen. De beregnes en gang i
    # __post_init__, så resten af programmet kan læse dem som almindelige
    # attributter uden at regne noget ud selv.
    hour: int = field(init=False)
    weekday: str = field(init=False)
    date: str = field(init=False)
    ip_scope: str = field(init=False)
    service: str = field(init=False)
    event_category: str = field(init=False)
    status_category: str = field(init=False)

    # Kører automatisk lige efter et LogRecord er oprettet, og udfylder de beregnede felter
    def __post_init__(self):
        self.hour = self.timestamp.hour
        self.weekday = WEEKDAYS[self.timestamp.weekday()]
        self.date = self.timestamp.date().isoformat()
        self.ip_scope = classify_ip(self.src_ip)
        self.service = service_name(self.dest_port)
        self.event_category = categorize_event(self.event)
        self.status_category = categorize_status(self.status)
