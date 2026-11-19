# Læseguide til Bumle Business

Guiden er skrevet til en læser, der ikke har set projektet før, og som vil læse hver linje kode. Den angiver en rækkefølge og begrunder, hvorfor netop den rækkefølge giver færrest fremmede navne undervejs. Guiden dækker den kørende kode: cirka 1.500 linjer Python fordelt på 16 filer. Tests, værktøjer og præsentationer er holdt ude.

Alle stier er skrevet fra repoets rod, også selv om denne fil ligger i `presentation/`.

## Principperne bag rækkefølgen

Fire regler styrer rækkefølgen. De er ikke originale, men de forklarer hvert valg nedenfor.

1. **Kontrakter før implementering.** Konstanter, fejltyper og datamodellen læses først. Alle andre filer taler om dem, så et navn som `LOG_COLUMNS`, `LogFileError` eller `record.ip_scope` er kendt, når det dukker op.
2. **Afhængigheder før afhængere.** En fil læses efter de filer, den importerer. Så står intet kald uforklaret, og man behøver ikke gætte, hvad en funktion gør, mens man læser den.
3. **Indgangspunktet efter delene.** `main.py` er sammensætning af de andre moduler. Læst til sidst i kernekoden bliver den en tjekliste, der bekræfter, at helheden er forstået.
4. **Præsentation efter beregning.** Visualiseringerne bygger på analysefunktionerne og på de grupperede rækker, så de kommer bagefter alt, hvad de viser.

## Rækkefølgen

| # | Fil | Linjer | Rolle og hvorfor netop her |
|---|---|---|---|
| 0.1 | `Opgave.md` | 42 | Opgaveformuleringen. Domænet og kravene kommer før løsningen. |
| 0.2 | `README.md` | 89 | Forfatternes eget overblik, mappestruktur, diagramvalg og fund. Læses som kort, ikke som sandhed. |
| 0.3 | `requirements.txt` | 4 | Viser de eksterne afhængigheder: dash og plotly. Resten af den kørende kode bruger standardbiblioteket. |
| 1.1 | `config.py` | 35 | Kolonneorden, kolonnebredder og detektionsregler. Ingen logik, men alle filer læser herfra. |
| 1.2 | `errors.py` | 18 | Fire fejlklasser. De kastes i `loader.py`, `parser.py` og `dashboard.py` og fanges i `main.py`. |
| 1.3 | `model.py` | 97 | `LogRecord` og de rene hjælpefunktioner. De beregnede felter i `__post_init__` er hele kodens ordforråd. |
| 1.4 | `cyber_security_log_sample.txt` (første 20-30 linjer) | 541 | Inputformatet. Læs nok linjer til at se feltordenen. Resten er data, ikke kode. |
| 2.1 | `loader.py` | 33 | Fil til liste af tekstlinjer. Afgrænser, hvad der overhovedet kan gå galt før parsning. |
| 2.2 | `parser.py` | 48 | Linje til `LogRecord`, plus kontrakten med de oversprungne linjer. |
| 3.1 | `aggregation/counts.py` | 66 | Simpel optælling pr. level, event, status og bruger, og fejlraten for login. Mindst central af aggregeringerne, men nævnes først fordi `main.py` kalder den først. |
| 3.2 | `aggregation/grouped_counts.py` | 51 | Knudepunktet: grupperede rækker pr. bruger, IP, vært og port. Bruges af terminaltabellerne og af top-10-listerne. |
| 3.3 | `aggregation/user_ips.py` | 53 | Unikke brugere og IP'er til overbliksfanen, plus en teksttabel. Selvstændig, men hører til samme lag. |
| 3.4 | `console/tables.py` | 35 | Lukker terminalvejen. Tager de grupperede rækker og skriver dem som tekst. |
| 4.1 | `analysis.py` | 166 | Alle beregninger til dashboardet: top-10, fejlrate pr. bruger, timefordeling, portserier. Rene funktioner over `LogRecord`. |
| 4.2 | `detection/suspicious_accounts.py` | 69 | Regelbaseret detektion. Bruger `config.SUS_DETECTION` og `record.ip_scope`, som nu er kendte. |
| 5.1 | `main.py` | 121 | Indgangen. De fire nummererede trin i `main()` svarer til faserne 2 til 4. Læses som sammensætning, ikke som ny kode. |
| 6.1 | `visualization/tables.py` | 128 | Plotly-tabeller og kolonnenavne. Løv i visualiseringen, importerer kun `config`. |
| 6.2 | `visualization/logview.py` | 70 | Filtrering og sortering af logtabellen. Importerer `tables`. |
| 6.3 | `visualization/bar_chart.py` | 44 | Søjlediagrammet. Lille og selvstændigt. |
| 6.4 | `visualization/scatter_plots.py` | 172 | De tre punktdiagrammer og `build_figures()`. Bygger på `analysis`. |
| 6.5 | `visualization/dashboard.py` | 287 | Dash-appen med faner, filtre og callback. Sidste fil, fordi den samler alt det foregående. |

## Fase 0: Kortet før terrænet

`Opgave.md` beskriver en virksomhed, der vil have VPN-logge gjort læsbare og undersøgelige, og stiller krav om indlæsning, tabelvisning, sammenhænge via scatter-plots og generel visualisering. Den læses først, fordi den forklarer, hvorfor programmet overhovedet findes, og hvilke dele der er krav og hvilke der er valg.

`README.md` er forfatternes egen vejvisning. Den rummer mappestrukturen, en tabel over diagramvalg med begrundelser, detektionsreglernes formål og en beskrivelse af fundet i loggen. Den er nyttig som ramme, men skal læses med forbehold: den er skrevet ved siden af koden, ikke genereret fra den, og enkelte detaljer kan være forældede. Man opdager det først, når koden er læst, hvilket er endnu en grund til at tage den tidligt og kontrollere den undervejs.

Afhængighedsfilen er på fire linjer og fortæller noget vigtigt om projektets karakter: kun visualiseringen kræver installation. Indlæsning, parsning, aggregering og detektion er skrevet med standardbiblioteket.

## Fase 1: Ordforrådet

De tre første filer indeholder næsten ingen kontrolflow, men de definerer de navne, som resten af koden bruger. Læses de først, slipper man for at standse op senere for at slå op, hvad en konstant betyder.

`config.py` fastlægger feltordenen i en loglinje (`LOG_COLUMNS`), som er den kontrakt `parser.py` implementerer. Den indeholder også `SUS_DETECTION`, altså hvilke eventtyper der tælles, og hvor mange gange de skal optræde, før en bruger flagges. Det er den eneste fil, hvor forretningsreglerne kan ændres uden at røre logik.

`errors.py` er atten linjer og består af en basisklasse og tre undertyper. Den lille fil gør en stor forskel senere: `main.py` fanger `BumleBusinessError` og printer en kort besked i stedet for et traceback, mens de tre undertyper viser, hvilket lag der fejlede.

`model.py` er kodens vigtigste fil. `LogRecord` har ni felter, der kommer direkte fra loglinjen, og syv beregnede felter, som `__post_init__` udfylder: time, ugedag, dato, IP-område, servicenavn og de to kategorier for event og status. Pointen er, at resten af programmet aldrig regner noget ud selv. Når `analysis.py` spørger om `record.ip_scope == "ekstern"`, eller `detection` spørger om `record.event_category`, er svaret allerede beregnet. Derfor er `model.py` også stedet, hvor begreberne `intern`, `ekstern`, `succes`, `fejl` og `neutral` får deres præcise betydning, og det er den betydning, alle senere filer bygger videre på.

Logfilen læses til sidst i fasen, og kun de første tyve til tredive linjer. Formatet er `nøgle=værdi` otte gange efterfulgt af `msg="..."`, og det er den form, `parser.py` skal håndtere. De resterende 500 linjer er de data, fundet i README handler om. Man kan vende tilbage til dem, når detektionen er læst, hvis man vil se, om reglerne faktisk fanger det, README påstår.

## Fase 2: Indlæsningsvejen fra fil til record

Her begynder koden at gøre noget, og rækkefølgen følger data: fil, linjer, record.

`loader.py` har ansvaret for alt, der kan gå galt før parsning: stien findes ikke, stien er en mappe, filen er tom, filen er ikke UTF-8, og der mangler læserettigheder. Hver fejl oversættes til `LogFileError`, så `main.py` kan vise en forståelig besked. Filen er kort, men den forklarer, hvorfor `errors.py` findes.

`parser.py` er projektets mest kompakte fil og den, der er lettest at læse forkert. Otte felter splittes på mellemrum og deles ved lighedstegn, mens `msg` hentes med et split ved `msg=` og renses for citationstegn, fordi beskeden kan indeholde mellemrum. Vigtigst er returværdien: de records, der kunne læses, og de linjer, der blev sprunget over. Den kontrakt gør, at en dårlig linje ikke stopper hele programmet, og den dukker op igen i `main.py` som `skipped_lines`.

## Fase 3: Aggregeringslaget

Tre filer under `aggregation/` besvarer tre forskellige spørgsmål om de samme records, og de læses i den rækkefølge, `main.py` bruger dem.

`counts.py` tæller forekomster pr. bruger, level, event og status og returnerer desuden andelen af fejlede loginforsøg. Den er den mindst centrale af de tre, og den eneste fil i projektet med et dobbeltløkke over alle records for hver unik værdi. Det er værd at bemærke som et stilbrud, ikke som en fejl, fordi loggen er lille.

`grouped_counts.py` er knudepunktet. Den bygger fire dictionaries, en pr. gruppering, og opdaterer dem i samme gennemløb. Resultatet er en lang liste af dictionaries, hvor hver række har en nøgle som `User`, `src_ip`, `dest_host` eller `dest`, plus optællinger. Både terminaltabellerne og `analysis.top_n_lists` læser denne liste, så filen forklarer, hvorfor de to visninger viser de samme tal.

`user_ips.py` gør noget andet: den bruger mængder til at tælle unikke brugere og IP'er og til at se, hvor mange IP'er hver bruger har haft. Den er selvstændig og bruges kun af dashboardets overbliksfane, men den hører til samme lag og læses derfor her.

`console/tables.py` lukker terminalvejen. Den filtrerer rækker, beregner kolonnebredder ud fra det længste indhold og skriver tabellen både til skærmen og til `printFilteredTable.txt`. Den er også den fil, der forklarer, hvorfor `printFilteredTable.txt` ligger i repoet.

## Fase 4: Analyse og detektion

`analysis.py` er den største beregningsfil og den, dashboardet hviler på. Den definerer `is_failure`, som er den eneste definition af, hvad en fejl er: enten er eventet i fejlkategorien, eller også er status det. Den samme funktion bruges af fejlraten pr. bruger, af fejlandelen pr. port og af overblikket. Resten af filen er rene funktioner, der returnerer lister og dictionaries og aldrig skriver til konsollen, hvilket er forudsætningen for, at både CLI og dashboard kan bruge dem. `TypedDict`-klasserne i toppen er filens egen dokumentation af returformerne og gør det lettere at læse visualiseringskoden bagefter.

`detection/suspicious_accounts.py` læses efter analysen, fordi den også arbejder over hele loggen, men med en anden logik. Den sorterer efter tid, tæller kun events fra interne IP'er og kun de eventtyper, der står i `config.SUS_DETECTION`. Når tærsklen er nået, finder den det første brud og derefter næste sted, samme IP dukkede op på en anden vært eller port. Det er den eneste fil, hvor rækkefølgen i tid betyder noget for resultatet, og den forklarer den tekst, `main.py` printer til sidst.

## Fase 5: Indgangen

`main.py` læses først, når delene er kendt. Filen har fire små funktioner, der hver især er trivielle efter fase 2 til 4: terminalbredde, de to tabeludskrifter og argumentparsning. Hovedfunktionen er den interessante, fordi dens fire nummererede kommentarer svarer til de tre foregående faser: læs filen, parse linjerne, tæl events, gruppér rækker. Læst her virker den som en tjekliste, der bekræfter helheden, og man ser samtidig, at fejlhåndteringen kun findes to steder: omkring indlæsning og parsning, og omkring opstart af dashboardet.

## Fase 6: Visualiseringen

Rækkefølgen i denne fase er bestemt af imports, ikke af, hvor spændende filerne er.

`visualization/tables.py` er løvet. Den importerer kun `config`, definerer kolonnenavne og tomme-tabel-tekster og bygger Plotly-tabeller. `logview.py` importerer `tables` og tilføjer filtrering og sortering, altså den eneste logik i visningen, der ikke er layout. `bar_chart.py` og `scatter_plots.py` er uafhængige af de to og bygger på `analysis`. `dashboard.py` kommer sidst, fordi den importerer alle fire, `analysis` og `user_ips` og samler dem i faner, filtre og callbacks. Læst før de andre ville den være en lang liste af ukendte navne; læst efter er den en oversigt over, hvordan delene sættes sammen.

## Kort rute, hvis tiden er knap

Kan man ikke læse alt, dækker fem filer næsten hele arkitekturen: `model.py` (ordforrådet), `parser.py` (input), `aggregation/grouped_counts.py` (grupperingen), `analysis.py` (beregningerne) og `main.py` (sammenhængen). Læs dem i den rækkefølge. Visualiseringen kan tilføjes som enkeltstående filer bagefter, uden at det ændrer forståelsen af kernekoden.
