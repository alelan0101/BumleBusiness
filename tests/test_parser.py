from datetime import datetime

import pytest

from loader import load_log_file
from parser import log_line_parser

MISSING_FIELD_LINE = (
    "2026-03-02T09:25:00 level=INFO event=VPN_CONNECT user=ida src_ip=10.0.0.9 "
    'dest_port=443 status=OK msg="Missing host field"'
)
INVALID_PORT_LINE = (
    "2026-03-02T09:30:00 level=INFO event=VPN_CONNECT user=ida src_ip=10.0.0.9 "
    'dest_host=vpn01 dest_port=HTTPS status=OK msg="Invalid port value"'
)
MISSING_MSG_LINE = (
    "2026-03-02T09:35:00 level=INFO event=VPN_CONNECT user=ida src_ip=10.0.0.9 "
    "dest_host=vpn01 dest_port=443 status=OK"
)
INVALID_TIMESTAMP_LINE = (
    "2026-13-45T99:99:99 level=INFO event=VPN_CONNECT user=ida src_ip=10.0.0.9 "
    'dest_host=vpn01 dest_port=443 status=OK msg="Invalid timestamp"'
)


# Alle linjer i loguddraget parses, og ingen ender i skipped_lines.
def test_parses_every_line_in_excerpt(small_log_lines: list[str]):
    records, skipped_lines = log_line_parser(small_log_lines)

    assert skipped_lines == []
    assert len(records) == len(small_log_lines)


# De 9 logfelter mappes korrekt, inkl. datetime og int-konvertering.
def test_maps_all_nine_fields(small_log_lines: list[str]):
    record = log_line_parser(small_log_lines)[0][0]

    assert record.timestamp == datetime(2026, 3, 1, 8, 1, 17)
    assert record.level == "INFO"
    assert record.event == "LOGIN_SUCCESS"
    assert record.user == "eve"
    assert record.src_ip == "10.0.0.5"
    assert record.dest_host == "db01"
    assert record.dest_port == 53
    assert record.status == "OK"
    assert record.msg == "User authenticated successfully"


# msg med mellemrum skal blive ét felt og ikke sprede sig ud over linjen.
def test_msg_with_spaces_is_one_field(small_log_lines: list[str]):
    record = log_line_parser(small_log_lines)[0][3]

    assert record.msg == "Access denied to protected file"


# timestamp og dest_port får de rigtige typer, ikke rå strings.
def test_converts_timestamp_and_port_types(small_log_lines: list[str]):
    record = log_line_parser(small_log_lines)[0][0]

    assert isinstance(record.timestamp, datetime)
    assert isinstance(record.dest_port, int)


# Hele sample-filen (541 linjer) parses uden afvisninger.
def test_parses_all_541_lines_from_default_file():
    records, skipped_lines = log_line_parser(load_log_file())

    assert len(records) == 541
    assert skipped_lines == []


# Tom msg er gyldig og bliver en tom streng, ikke en afvist linje.
def test_empty_msg_is_kept_as_empty_string(edge_case_lines: list[str]):
    records, _ = log_line_parser(edge_case_lines)

    assert records[0].msg == ""


# Citationstegn inde i msg bevares, kun de ydre fjernes.
def test_quotes_inside_msg_are_preserved(edge_case_lines: list[str]):
    records, _ = log_line_parser(edge_case_lines)

    assert records[1].msg == 'Changed rule "deny-all" on fw01'


# Afviste linjer returneres uændret, så de kan rapporteres bagefter.
def test_skipped_lines_are_returned_unchanged(edge_case_lines: list[str]):
    _, skipped_lines = log_line_parser(edge_case_lines)

    assert skipped_lines == edge_case_lines[2:]
    assert all(isinstance(line, str) for line in skipped_lines)


# Hver enkelt fejltype afvises isoleret: manglende felt, ugyldig port,
# manglende msg og ugyldigt timestamp.
@pytest.mark.parametrize(
    "line",
    [
        pytest.param(MISSING_FIELD_LINE, id="manglende-felt"),
        pytest.param(INVALID_PORT_LINE, id="ugyldig-port"),
        pytest.param(MISSING_MSG_LINE, id="manglende-msg"),
        pytest.param(INVALID_TIMESTAMP_LINE, id="ugyldigt-timestamp"),
    ],
)
def test_invalid_line_is_skipped(line: str):
    records, skipped_lines = log_line_parser([line])

    assert records == []
    assert skipped_lines == [line]


# msg= uden citationstegn og uden indhold giver også en tom streng.
def test_unquoted_empty_msg_is_kept_as_empty_string():
    line = (
        "2026-03-02T10:00:00 level=INFO event=VPN_CONNECT user=ida src_ip=10.0.0.9 "
        "dest_host=vpn01 dest_port=443 status=OK msg="
    )

    records, skipped_lines = log_line_parser([line])

    assert skipped_lines == []
    assert records[0].msg == ""


# Tom input giver tomme lister i stedet for fejl.
def test_empty_input_returns_empty_lists():
    assert log_line_parser([]) == ([], [])
