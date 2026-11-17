import shutil
import subprocess
import sys
from argparse import ArgumentParser, Namespace
from collections import Counter
from pathlib import Path

import parser
from aggregation import counts, grouped_counts, row_values, user_ips
from config import APP_NAME, APP_VERSION, BASE_DIR, DEFAULT_LOG_PATH
from console import tables
from detection import suspicious_accounts
from errors import BumleBusinessError
from loader import load_log_file
from visualization import dashboard

width = shutil.get_terminal_size().columns
def general_terminal_table(Compiled_Data):
    print("General Observations for regular useful user data")
    print("_" * width)
    filter_keys = ["User","Events","Level","Status"]
    tables.Sort_And_Table(Compiled_Data, filter_keys)

def port_watch(Compiled_Data):
    filter_keys = ["dest","ALERT","WARN","MALWARE_SIGNATURE_MATCH"]
    print("Malware/Warning Tale")
    print("_" * width)
    tables.Sort_And_Table(Compiled_Data, filter_keys)


TEST_DIR = BASE_DIR / "tests"


def parse_args(argv: list[str] | None = None) -> Namespace:
    parser = ArgumentParser(description=f"{APP_NAME} - VPN-logovervågning")
    parser.add_argument(
        "--log-file",
        type=Path,
        default=DEFAULT_LOG_PATH,
        help="Sti til logfilen der skal indlæses",
    )
    parser.add_argument(
        "--run-tests",
        action="store_true",
        help="Kør testsuiten med pytest og afslut",
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Vis coverage sammen med --run-tests",
    )
    parser.add_argument(
        "--dashboard",
        action="store_true",
        help="Start dashboardet med tabel og diagrammer efter kørsel",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=dashboard.DEFAULT_PORT,
        help="Port til dashboardet",
    )
    return parser.parse_args(argv)


def run_tests(coverage: bool = False) -> int:
    command = [sys.executable, "-m", "pytest", str(TEST_DIR)]
    if coverage:
        command += ["--cov=parser", "--cov=model", "--cov=loader", "--cov-report=term-missing"]
    return subprocess.run(command, check=False).returncode


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if args.run_tests:
        return run_tests(args.coverage)

    try:
        lines = load_log_file(args.log_file)
        records, skipped_lines = parser.log_line_parser(lines)
        event_count = Counter(record.event for record in records)
        labels = list(event_count.keys())
        values = list(event_count.values())
        print("Labels: ", labels)
        print("Values: ", values)
        AllData, LoginProcent = counts.filtering(records)
        Keys = AllData[2].keys()
        print(Keys)
        Compiled_Data = grouped_counts.highestTabel(AllData, records)
        print(records[100].event)
        # This thing lets you filter the stuff, you can copy paste it and change in the [] area to change what you filter for
        converted = row_values.convert_from_Complied_Data(
            Compiled_Data, ["User", "LOGIN_FAILED"]
        )
        # This thing prints the general info table
        general_terminal_table(Compiled_Data)
        print('=' * width)
        # This thing prints the malware/port watch table
        port_watch(Compiled_Data)
        print('=' * width)
        Summary = user_ips.get_user_ip_summary(records)
        SummaryTable = user_ips.format_user_ip_table(Summary)
        Malware = suspicious_accounts.track_suspicious_accounts(records)
        print(Malware)
    except BumleBusinessError as error:
        print(f"Fejl: {error}")
        return 1

    print(f"{APP_NAME} {APP_VERSION}")
    print(f"Indlæste {len(records)} linjer fra {args.log_file}")

    if skipped_lines:
        print(f"Sprang {len(skipped_lines)} ugyldige linjer over")

    if args.dashboard:
        dashboard.run(records, args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
