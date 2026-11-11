import subprocess
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path

import parser
from config import APP_NAME, APP_VERSION, BASE_DIR, DEFAULT_LOG_PATH
from errors import BumleBusinessError
from loader import load_log_file

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
    except BumleBusinessError as error:
        print(f"Fejl: {error}")
        return 1

    print(f"{APP_NAME} {APP_VERSION}")
    print(f"Indlæste {len(records)} linjer fra {args.log_file}")

    if skipped_lines:
        print(f"Sprang {len(skipped_lines)} ugyldige linjer over")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
