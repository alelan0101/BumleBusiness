from argparse import ArgumentParser, Namespace
from pathlib import Path

import parser, stats, filterForHighest
from config import APP_NAME, APP_VERSION, DEFAULT_LOG_PATH
from errors import BumleBusinessError
from loader import load_log_file


def parse_args(argv: list[str] | None = None) -> Namespace:
    parser = ArgumentParser(description=f"{APP_NAME} - VPN-logovervågning")
    parser.add_argument(
        "--log-file",
        type=Path,
        default=DEFAULT_LOG_PATH,
        help="Sti til logfilen der skal indlæses",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    try:
        lines = load_log_file(args.log_file)
        records, skipped_lines = parser.log_line_parser(lines)
        AllData, LoginProcent = stats.filtering(records)
        filterForHighest.highestTabel(AllData,records)
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
