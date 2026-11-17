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

# Terminalens bredde i tegn, så stregerne under overskrifterne passer til vinduet
width = shutil.get_terminal_size().columns


# Printer den første tabel i terminalen: en række pr. bruger med antal
# events, level og status
#
# filter_keys er de kolonner der vises, i den rækkefølge de skal stå
def general_terminal_table(Compiled_Data):
    print("General Observations for regular useful user data")
    print("_" * width)

    filter_keys = ["User","Events","Level","Status"]
    tables.Sort_And_Table(Compiled_Data, filter_keys)


# Printer den anden tabel: hvor mange advarsler og malware-fund der er pr.
# destination. "dest" er porten med servicenavn, fx "443 (HTTPS)".
def port_watch(Compiled_Data):
    filter_keys = ["dest","ALERT","WARN","MALWARE_SIGNATURE_MATCH"]
    print("Malware/Warning Tale")
    print("_" * width)

    tables.Sort_And_Table(Compiled_Data, filter_keys)


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
# terminalen, og returnerer pytest's exitkode
#
# --coverage tilføjer de flag der får pytest-cov til at vise en rapport
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
        # 1) Læs filen som en liste af tekstlinjer
        lines = load_log_file(args.log_file)

        # 2) Del hver linje op i felter og lav et LogRecord
        records, skipped_lines = parser.log_line_parser(lines)

        # 3) Tæl events pr. bruger, level, event og status
        AllData, _ = counts.filtering(records)

        # 4) Grupper de samme records pr. bruger, IP, vært og port. Det er
        #    disse rækker tabellerne nedenfor bygger på.
        Compiled_Data = grouped_counts.highestTabel(AllData, records)

        # Eksempel på at hente enkelte værdier ud af tabellen: her brugere og
        # deres antal LOGIN_FAILED. Skift teksten i listen for at hente andre
        # kolonner; resultatet bruges ikke videre her.
        # converted = row_values.convert_from_Complied_Data(
        #     Compiled_Data, ["User", "LOGIN_FAILED"]
        # )

        # Print de to tabeller i terminalen, med en streg imellem
        general_terminal_table(Compiled_Data)
        print('=' * width)
        port_watch(Compiled_Data)
        print('=' * width)

        # Opsummering af unikke brugere og IP'er pr. bruger. Tabellen bygges,
        # men printes ikke her.
        # Summary = user_ips.get_user_ip_summary(records)
        # SummaryTable = user_ips.format_user_ip_table(Summary)

        # Kig efter konti der gentagne gange gør noget mistænkeligt
        Malware = suspicious_accounts.track_suspicious_accounts(records)
        print(Malware)
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
        dashboard.run(records, args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
