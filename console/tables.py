"""Udskrivning af grupperede rækker som konsolttabel."""


# Printer en tabel over de grupperede rækker og gemmer den samme tabel i filen printFilteredTable.txt.
# Keys bestemmer hvilke kolonner der vises, fx ["User", "Events", "Level", "Status"].
def print_table(compiled_data, keys):
    # Hvis tabellen viser brugere eller porte, filtreres rækkerne for IP'er og værter fra, så de ikke blander sig i tabellen
    row_keys = [key for key in ("User", "dest") if key in keys]

    # Samme som dette, måske lettere at læse:
    # row_keys = []
    # for key in ("User", "dest"):
    #     if key in keys:
    #         row_keys.append(key)

    if row_keys:
        compiled_data = [
            record
            for record in compiled_data
            if any(key in record for key in row_keys)
        ]

        # Samme som dette, måske lettere at læse:
        # filtered_data = []
        # for record in compiled_data:
        #     matches = False
        #     for key in row_keys:
        #         if key in record:
        #             matches = True
        #     if matches:
        #         filtered_data.append(record)
        # compiled_data = filtered_data

    # Lav tabellen om til tekst. Mangles en værdi, vises "N/A".
    rows = [
        [str(record.get(key, "N/A")) for key in keys]
        for record in compiled_data
    ]

    # Samme som dette, måske lettere at læse:
    # rows = []
    # for record in compiled_data:
    #     row = []
    #     for key in keys:
    #         row.append(str(record.get(key, "N/A")))
    #     rows.append(row)

    # Bredden på hver kolonne er længden af den længste tekst, header medregnet
    widths = [
        max([len(key)] + [len(row[index]) for row in rows])
        for index, key in enumerate(keys)
    ]

    # Samme som dette, måske lettere at læse:
    # widths = []
    # for index, key in enumerate(keys):
    #     lengths = [len(key)]
    #     for row in rows:
    #         lengths.append(len(row[index]))
    #     widths.append(max(lengths))

    header = " | ".join(
        key.ljust(widths[index]) for index, key in enumerate(keys)
    )

    # Samme som dette, måske lettere at læse:
    # parts = []
    # for index, key in enumerate(keys):
    #     parts.append(key.ljust(widths[index]))
    # header = " | ".join(parts)

    separator = "-+-".join("-" * width for width in widths)

    # Samme som dette, måske lettere at læse:
    # parts = []
    # for width in widths:
    #     parts.append("-" * width)
    # separator = "-+-".join(parts)

    table_rows = [
        " | ".join(value.ljust(widths[index]) for index, value in enumerate(row))
        for row in rows
    ]

    # Samme som dette, måske lettere at læse:
    # table_rows = []
    # for row in rows:
    #     parts = []
    #     for index, value in enumerate(row):
    #         parts.append(value.ljust(widths[index]))
    #     table_rows.append(" | ".join(parts))
    table = "\n".join([header, separator, *table_rows])

    # Gem tabellen i en fil, så den kan åbnes bagefter, og print den også
    with open("printFilteredTable.txt", mode="w", encoding="utf-8") as output:
        output.write(f"{table}\n")

    print(table)
