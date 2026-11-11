from datetime import datetime

import pytest

from model import (
    LogRecord,
    categorize_event,
    categorize_status,
    classify_ip,
    service_name,
)


# Bygger en gyldig record, så hver test kun ændrer det felt den tester.
def make_record(**overrides) -> LogRecord:
    fields = {
        "timestamp": datetime(2026, 3, 2, 14, 30),
        "level": "INFO",
        "event": "LOGIN_SUCCESS",
        "user": "ida",
        "src_ip": "10.0.0.5",
        "dest_host": "vpn01",
        "dest_port": 80,
        "status": "FAILED",
        "msg": "Test",
    }
    fields.update(overrides)
    return LogRecord(**fields)


# RFC1918-grænserne: 10/8, 172.16-31 og 192.168/16 er interne, resten eksterne.
# Parametrene dækker både grænseværdier og adresser lige uden for intervallerne.
@pytest.mark.parametrize(
    ("address", "expected"),
    [
        pytest.param("10.0.0.1", "intern", id="10.0.0.1"),
        pytest.param("10.255.255.255", "intern", id="10.255.255.255"),
        pytest.param("172.15.255.255", "ekstern", id="172.15.255.255"),
        pytest.param("172.16.0.0", "intern", id="172.16.0.0"),
        pytest.param("172.31.255.255", "intern", id="172.31.255.255"),
        pytest.param("172.32.0.0", "ekstern", id="172.32.0.0"),
        pytest.param("192.168.0.1", "intern", id="192.168.0.1"),
        pytest.param("192.168.255.255", "intern", id="192.168.255.255"),
        pytest.param("192.169.0.1", "ekstern", id="192.169.0.1"),
        pytest.param("8.8.8.8", "ekstern", id="8.8.8.8"),
    ],
)
def test_classify_ip(address: str, expected: str):
    assert classify_ip(address) == expected


# Ugyldige IP-strenge må ikke crashe klassificeringen og får deres egen værdi.
@pytest.mark.parametrize(
    "address",
    ["10.0.0", "10.0.0.0.1", "ikke-en-ip", "", "::1", "256.1.1.1"],
)
def test_classify_invalid_ip(address: str):
    assert classify_ip(address) == "invalid"


# Oktetter over 255 må ikke blive interne, selv om præfikset ser privat ud.
@pytest.mark.parametrize("address", ["10.0.0.999", "172.16.0.256", "192.168.1.300"])
def test_classify_out_of_range_octet_as_invalid(address: str):
    assert classify_ip(address) == "invalid"


# Kendte porte mappes til servicenavne; alle andre give "Ukendt".
@pytest.mark.parametrize(
    ("port", "expected"),
    [
        pytest.param(22, "SSH", id="22"),
        pytest.param(25, "SMTP", id="25"),
        pytest.param(53, "DNS", id="53"),
        pytest.param(80, "HTTP", id="80"),
        pytest.param(443, "HTTPS", id="443"),
        pytest.param(445, "SMB", id="445"),
        pytest.param(3389, "RDP", id="3389"),
        pytest.param(8080, "HTTP-ALT", id="8080"),
        pytest.param(1234, "Ukendt", id="ukendt-port"),
        pytest.param(0, "Ukendt", id="port-0"),
    ],
)
def test_service_name(port: int, expected: str):
    assert service_name(port) == expected


# Kun LOGIN_SUCCESS er succes, LOGIN_FAILED er fejl, resten er neutral.
@pytest.mark.parametrize(
    ("event", "expected"),
    [
        pytest.param("LOGIN_SUCCESS", "succes", id="login-success"),
        pytest.param("LOGIN_FAILED", "fejl", id="login-failed"),
        pytest.param("VPN_CONNECT", "neutral", id="vpn-connect"),
        pytest.param("PORT_SCAN_DETECTED", "neutral", id="port-scan"),
        pytest.param("", "neutral", id="tom"),
    ],
)
def test_categorize_event(event: str, expected: str):
    assert categorize_event(event) == expected


# OK er succes, FAILED og BLOCKED er fejl, ukendte statusser er neutrale.
@pytest.mark.parametrize(
    ("status", "expected"),
    [
        pytest.param("OK", "succes", id="ok"),
        pytest.param("FAILED", "fejl", id="failed"),
        pytest.param("BLOCKED", "fejl", id="blocked"),
        pytest.param("PENDING", "neutral", id="pending"),
        pytest.param("", "neutral", id="tom"),
    ],
)
def test_categorize_status(status: str, expected: str):
    assert categorize_status(status) == expected


# hour, weekday og date udledes af timestamp (2026-03-02 er en mandag).
def test_record_derives_time_fields():
    record = make_record(timestamp=datetime(2026, 3, 2, 14, 30))

    assert record.hour == 14
    assert record.weekday == "mandag"
    assert record.date == "2026-03-02"


# Ugedagsnavnene er på dansk, og søndag er det sidste element i WEEKDAYS.
def test_record_derives_sunday():
    record = make_record(timestamp=datetime(2026, 3, 1, 8, 0))

    assert record.weekday == "søndag"


# LogRecord beriger selv med IP-scope, service og de to kategorier.
def test_record_derives_enriched_fields():
    record = make_record()

    assert record.ip_scope == "intern"
    assert record.service == "HTTP"
    assert record.event_category == "succes"
    assert record.status_category == "fejl"


# Ekstern IP og en port uden service skal også give forventede værdier.
def test_record_derives_external_scope_and_unknown_service():
    record = make_record(src_ip="203.0.113.7", dest_port=1234)

    assert record.ip_scope == "ekstern"
    assert record.service == "Ukendt"


# En ugyldig src_ip giver ip_scope "invalid" på recorden.
def test_record_derives_invalid_scope():
    record = make_record(src_ip="10.0.0.999")

    assert record.ip_scope == "invalid"
