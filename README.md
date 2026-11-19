# Bumle Business – VPN-logovervågning

Repository: <https://github.com/alelan0101/BumleBusiness>

## Introduktion

Projektets formål er at gøre de rå logdata læsbare og sammenlignelige. Loggen indlæses i hukommelsen, vises i tabeller og visualiseres i diagrammer, så mistænkelig aktivitet kan findes og undersøges.

## Overblik

`analysis.py` beregner top-10 lister og de dataserier, som diagrammerne bygger på. Funktionerne returnerer lister og dictionaries og skriver ikke selv til konsollen, så de kan genbruges af både CLI, dashboard og plot. Top-10-listerne bygger på `grouped_counts.grouped_rows` i `aggregation/`, som grupperer events pr. bruger, kilde-IP, destinationsvært og port. Konsoltabellerne bygges af `console/tables.py`.

### Detektion af mistænkelige konti

`detection/suspicious_accounts.py` holder øje med de eventtyper, der står i `config.SUS_DETECTION`: `ALERT` og `MALWARE_SIGNATURE_MATCH`. For hver bruger tæller programmet events fra interne IP'er og beskriver, hvor det først skete, og hvad samme IP gjorde bagefter, når tærsklen er nået. Fundene printes i terminalen under tabellerne.

Login-forsøg indgår ikke i detektionsreglerne, men de tælles i tabellerne og i fejlraten pr. bruger. `counts.count_by_field()` returnerer andelen af fejlede loginforsøg som anden returværdi, og den printes i terminalen. Mange fejlede logins efterfulgt af et vellykket login eller et password-reset er et typisk tegn på mistænkelig aktivitet.

#### Fundet

Ifølge den indhentning, der er lavet, er det første brud sket på walter. Det ses blandt andet ved, at han har flest fejl, og at mange af dem er login_failed. Derefter kommer en user authentication fra den IP, og gennem de IP-spor, programmet udskriver, er det muligt at følge, hvordan den hopper rundt og ender med admin password. Den IP, 172.16.0.44, har en malware match, og senere en reset på admin password.

### Kørsel

Kør kommandoerne fra repoets rod. Afhængighederne installeres fra `requirements.txt`:

```bash
pip install -r requirements.txt
python main.py
python main.py --dashboard 
```

Dashboardet åbner på `http://127.0.0.1:8050`. Flagene er:

| Flag | Betydning |
|---|---|
| `--log-file STI` | Vælg en anden logfil end `cyber_security_log_sample.txt` |
| `--dashboard` | Start dashboardet efter tabellerne er printet |
| `--port PORT` | Port til dashboardet (standard 8050) |
| `--run-tests` | Kør testsuiten med pytest og afslut |
| `--coverage` | Vis coverage sammen med `--run-tests` |

Dashboardet har faner til logtabellen, overblikket, de fire diagrammer, fejlandel pr. port og top-10-listerne for brugere, kilde-IP'er og destinationsværter. Overbliksfanen viser periode, fejlrate og antal unikke brugere og IP'er fra `user_ips.get_user_ip_summary()`. `scatter_plots.build_figures(records)` returnerer de tre scatter-figurer, `bar_chart.event_bar_chart(records)` giver søjlediagrammet, `analysis.port_failure_rows()` leverer tallene til port-tabellen, og `tables.build_columns_table()` og `tables.build_top_n_table()` bygger tabellerne.

### Mappestruktur

| Mappe | Fil | Indhold |
|---|---|---|
| `aggregation/` | `grouped_counts.py` | Gruppering og optælling pr. bruger, IP, vært og port |
| | `counts.py` | Optælling pr. level, event, status og bruger |
| | `user_ips.py` | Unikke brugere og IP'er pr. bruger |
| `console/` | `tables.py` | Konsoltabel af de grupperede rækker |
| `detection/` | `suspicious_accounts.py` | Regelbaseret detektion af mistænkelige konti |
| `visualization/` | `dashboard.py` | Dash-appen med faner, layout og callback til logtabellen |
| | `bar_chart.py` | Søjlediagram med antal events pr. eventtype |
| | `logview.py` | Filtrering og sortering af logtabellen |
| | `scatter_plots.py` | De tre scatter-plots og `build_figures()` |
| | `tables.py` | Plotly-tabeller: logtabel, top-10, fejlandel pr. port og tom tabel |
| `tests/` | `test_*.py`, `fixtures/` | Tests og loguddrag til parser, model og loader |
| root | `main.py` | Kommandolinjeflag, konsoltabeller og opstart af dashboardet |
| | `analysis.py` | Top-10, events pr. time, fejlandel pr. port og dataserier til plots |
| | `parser.py`, `loader.py`, `model.py` | Indlæsning, parsning og datamodel |
| | `errors.py`, `config.py` | Fejltyper og konstanter |

### Valg af diagramtype

| Kolonnepar | Diagram | Begrundelse |
|---|---|---|
| `hour` vs. antal events | Scatter med punkter | Begge akser er tal, og hver time er en måling. Søjler ville også virke, men scatter gør det muligt at aflæse enkeltpunkter og en eventuel tendens direkte. |
| `user` vs. andel fejl | Scatter, et punkt pr. bruger, med en stiplet linje for den samlede fejlrate | Brugerne er kategorier, så punkterne er ikke forbundet. Referencelinjen gør det muligt at se, hvilke brugere der ligger over og under gennemsnittet. |
| `dest_port` vs. eventtype og IP-klasse | Scatter med port på x-aksen, eventtype på y-aksen, boblestørrelse som antal og farve som IP-klasse | Fire variabler i et plot: port, kategori, antal og intern/ekstern. Portene står i numerisk rækkefølge med servicenavn, så aksen kan læses uden at slå portnumre op. |
| `event` vs. antal | Søjlediagram | Eventtyperne er kategorier, og højden på søjlerne gør dem direkte sammenlignelige. |

## Kaldgraf

`docs/callgraph.html` er en selvstændig interaktiv side med kaldgrafen for koden. Den har ti visninger: moduloverblik, hele grafen, CLI-flowet fra `main.main`, detektionen og seks visninger af dashboardet — `visualization.dashboard.create_app` selv og de fem faner logtabel, overblik, diagrammer, fejlandel pr. port og top 10. Klik på en boks for at fremhæve dens kald og kaldere, brug søgefeltet til at finde en funktion, og chip-rækken til at fremhæve et helt modul.

Siden bygges med `pyan3` og Graphviz:

```bash
pip install -r requirements-dev.txt
scoop install graphviz   # eller winget install Graphviz.Graphviz
python tools/callgraph.py
```

`tools/callgraph.py` finder selv projektets Python-filer (uden `tests/`), kører `pyan3`, filtrerer hver visning og tegner den med `dot`. Siden har ingen eksterne referencer, så den kan åbnes direkte fra disken og virker uden netværk. Visningerne styres af `VIEWS` i scriptet: hver visning angiver en eller flere startfunktioner og hvor mange kald den skal følge.

## Tests

Testene ligger i `tests/` og kræver Python 3.10 eller nyere, ligesom programmet, samt `pytest` og `pytest-cov` fra `requirements.txt`. Kør kommandoerne fra repoets rod.

```bash
python -m pytest
```

En enkelt fil eller et filter på testnavn (`-k` matcher en del af navnet):

```bash
python -m pytest tests/test_parser.py
python -m pytest tests/test_parser.py -k msg
```

Testene dækker `loader.py`, `parser.py` og `model.py`.

```bash
python -m pytest --cov=parser --cov=model --cov=loader --cov-report=term-missing
```

`main.py` kan køre de samme tests som `pytest` ovenfor; med `--coverage` kommer rapporten med:

```bash
python main.py --run-tests
python main.py --run-tests --coverage
```

Loguddragene ligger i `tests/fixtures/`: `small_log.txt` er et gyldigt udsnit af `cyber_security_log_sample.txt`, og `edge_cases.txt` indeholder linjer, der skal afvises (manglende felt, ugyldig port), og linjer med grænsetilfælde (tom `msg`, citationstegn i `msg`).

## SCRUM

https://github.com/users/alelan0101/projects/2

Projektet er gennemført i et Sprint med et fælles Task Board, hvor opgaverne er flyttet mellem swimlanes efterhånden som de blev taget og færdigjort.

Epics definerer de overordnede kravspecifikationer. Under dem ligger features, som beskriver, hvilke dele der skal udarbejdes for at opfylde kravene, og under hver feature ligger de tasks, der præciserer, hvad der skal udarbejdes for at opfylde en given kravspecifikation.

User stories er de ønsker, en bruger har til et givent produkt, fx "Som bruger ønsker jeg at kunne se loggen i en tabel, så jeg kan finde mistænkelige hændelser". Tasks bliver oprettet på baggrund af brugernes ønsker, og hver task knyttes til den user story, den er med til at opfylde. Acceptkriterier er de minimumskrav, der skal opnås, for at en user story er opfyldt, og de bruges både til at vurdere, om en task er færdig, og til at definere, hvornår en user story kan lukkes. Task boardet bruges til at uddelegere tasks. Her kan man se, hvor langt en person er med en given opgave, og hvilke opgaver der er næste skridt i sprintet.

## Konklusion

Løsningen indlæser `cyber_security_log_sample.txt`, parser hver linje til et `LogRecord` og præsenterer dataene i konsoltabeller og i et dashboard med logtabel, overblik, fire diagrammer, fejlandel pr. port og top-10-lister. Scatter-plots viser sammenhænge mellem tid, brugere, fejl, porte og IP-klasser, og valget af diagramtype er begrundet i tabellen ovenfor.

De vigtigste resultater er, at loggens 541 linjer kan gennemgås samlet, og at detektionen peger på walter som det første brud, følger IP'en 172.16.0.44 videre til et malware-match og til sidst til et reset af admin password. Dermed kan mistænkelig aktivitet lokaliseres uden at læse logfilen linje for linje.
