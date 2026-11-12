from argparse import ArgumentParser, Namespace
from pathlib import Path

import parser, stats, filterForHighest, conversionOfNumbers, high_filter_helper, user_ip_helper
from config import APP_NAME, APP_VERSION, DEFAULT_LOG_PATH
from errors import BumleBusinessError
from loader import load_log_file

import os

width = os.get_terminal_size().columns 
def general_terminal_table(Compiled_Data):
    print("General Observations for regular useful user data")
    print("_" * width)
    filter_keys = ["User","Events","Level","Status"]
    high_filter_helper.Sort_And_Table(Compiled_Data, filter_keys)

def port_watch(Compiled_Data):
    filter_keys = ["dest","ALERT","WARN","MALWARE_SIGNATURE_MATCH"]
    print("Malware/Warning Tale")
    print("_" * width)
    high_filter_helper.Sort_And_Table(Compiled_Data, filter_keys)

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
        Compiled_Data = filterForHighest.highestTabel(AllData,records)
        #This thing lets you filter the stuff, you can copy paste it and change in the [] area to change what you filter for
        converted = conversionOfNumbers.convert_from_Complied_Data(Compiled_Data, ["User"])
        #This thing prints the general info table
        general_terminal_table(Compiled_Data)
        print('=' * width)
        #This thing prints the malware/port watch table
        port_watch(Compiled_Data)
        print('=' * width)
        Summary = user_ip_helper.get_user_ip_summary(records)
        SummaryTable = user_ip_helper.format_user_ip_table(Summary)
        print(f"General procent fejl: {LoginProcent} som decimaltal")
        print(f"User Count: {Summary.get("user_count")}")
        print(f"IP Count: {Summary.get("unique_ip_count")}")
        print(SummaryTable)
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
