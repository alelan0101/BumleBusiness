def Sort_And_Table(Compiled_Data, Keys):
    row_keys = [key for key in ("User", "dest") if key in Keys]
    if row_keys:
        Compiled_Data = [
            record
            for record in Compiled_Data
            if any(key in record for key in row_keys)
        ]

    rows = [
        [str(record.get(key, "N/A")) for key in Keys]
        for record in Compiled_Data
    ]
    widths = [
        max([len(key)] + [len(row[index]) for row in rows])
        for index, key in enumerate(Keys)
    ]

    header = " | ".join(
        key.ljust(widths[index]) for index, key in enumerate(Keys)
    )
    separator = "-+-".join("-" * width for width in widths)
    table_rows = [
        " | ".join(value.ljust(widths[index]) for index, value in enumerate(row))
        for row in rows
    ]
    table = "\n".join([header, separator, *table_rows])

    with open("printFilteredTable.txt", mode="w", encoding="utf-8") as output:
        output.write(f"{table}\n")

    print(table)
