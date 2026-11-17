import shutil
import subprocess
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path

import parser
from aggregation import counts, grouped_counts
from config import APP_NAME, APP_VERSION, BASE_DIR, DEFAULT_LOG_PATH
from console import tables
from detection import suspicious_accounts
from errors import BumleBusinessError
from loader import load_log_file
from visualization import dashboard


# Terminalens bredde i tegn, så stregerne under overskrifterne passer til vinduet
def terminal_width() -> int:
    return shutil.get_terminal_size().columns


# Printer den første tabel i terminalen: en række pr. bruger med antal events, level og status.
def general_terminal_table(compiled_data):
    print("General Observations for regular useful user data")
    print("_" * terminal_width())
    tables.print_table(
        compiled_data,
        ["User", "Events", "Level", "Status"],
    )


# Printer den anden tabel: hvor mange advarsler og malware-fund der er pr. destination. "dest" er porten med servicenavn, fx "443 (HTTPS)".
def port_watch(compiled_data):
    print("Malware/Warning Tale")
    print("_" * terminal_width())
    tables.print_table(
        compiled_data,
        ["dest", "ALERT", "WARN", "MALWARE_SIGNATURE_MATCH"],
    )


TEST_DIR = BASE_DIR / "tests"


# Læser kommandolinjeflagene, fx --log-file og --dashboard.
# ArgumentParser sørger selv for --help og for at brokke sig over ukendte flag.
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


# Starter pytest som et separat program, som hvis kommandoen blev skrevet i
# terminalen, og returnerer pytest's exitkode.
# --coverage tilføjer de flag der får pytest-cov til at vise en rapport.
def run_tests(coverage: bool = False) -> int:
    command = [sys.executable, "-m", "pytest", str(TEST_DIR)]

    if coverage:
        command += [
            "--cov=parser",
            "--cov=model",
            "--cov=loader",
            "--cov-report=term-missing",
        ]
    return subprocess.run(command, check=False).returncode


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if args.run_tests:
        return run_tests(args.coverage)

    try:
        # 1) Læs filen som en liste af tekstlinjer
        lines = load_log_file(args.log_file)

        # 2) Del hver linje op i felter og lav et LogRecord
        records, skipped_lines = parser.log_line_parser(lines)

        # 3) Tæl events pr. bruger, level, event og status
        _, login_failure_rate = counts.count_by_field(records)

        # 4) Grupper de samme records pr. bruger, IP, vært og port. Det er
        #    disse rækker tabellerne nedenfor bygger på.
        compiled_data = grouped_counts.grouped_rows(records)

        # Print de to tabeller i terminalen, med en streg imellem
        general_terminal_table(compiled_data)
        print("=" * terminal_width())
        port_watch(compiled_data)
        print("=" * terminal_width())
        print(f"Andel fejlede loginforsøg: {login_failure_rate * 100:.1f} %")

        # Kig efter konti der gentagne gange gør noget mistænkeligt
        print()
        print("Mistænkelige konti")
        print("_" * terminal_width())
        print(suspicious_accounts.track_suspicious_accounts(records))
    except BumleBusinessError as error:
        # Forventede fejl, fx en manglende logfil, vises kort og programmet stopper
        print(f"Fejl: {error}")
        return 1

    # Hvilket program og hvor mange linjer der blev læst
    print(f"{APP_NAME} {APP_VERSION}")
    print(f"Indlæste {len(records)} linjer fra {args.log_file}")

    if skipped_lines:
        print(f"Sprang {len(skipped_lines)} ugyldige linjer over")

    if args.dashboard:
        try:
            dashboard.run(records, args.port)
        except BumleBusinessError as error:
            print(f"Fejl: {error}")
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
