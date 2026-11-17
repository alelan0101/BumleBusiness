"""Udskrivning af grupperede rækker som konsolttabel."""


# Printer en tabel over de grupperede rækker og gemmer den samme tabel i filen printFilteredTable.txt.
# Keys bestemmer hvilke kolonner der vises, fx ["User", "Events", "Level", "Status"].
def Sort_And_Table(Compiled_Data, Keys):
    # Hvis tabellen viser brugere eller porte, filtreres rækkerne for IP'er og værter fra, så de ikke blander sig i tabellen
    row_keys = [key for key in ("User", "dest") if key in Keys]
    if row_keys:
        Compiled_Data = [
            record
            for record in Compiled_Data
            if any(key in record for key in row_keys)
        ]

    # Lav tabellen om til tekst. Mangles en værdi, vises "N/A".
    rows = [
        [str(record.get(key, "N/A")) for key in Keys]
        for record in Compiled_Data
    ]
    # Bredden på hver kolonne er længden af den længste tekst, header medregnet
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

    # Gem tabellen i en fil, så den kan åbnes bagefter, og print den også
    with open("printFilteredTable.txt", mode="w", encoding="utf-8") as output:
        output.write(f"{table}\n")

    print(table)
