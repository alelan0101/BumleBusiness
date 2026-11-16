# Bumle Business – VPN-logovervågning

## Overblik

`analysis.py` beregner top-10 lister og de dataserier, som diagrammerne bygger på. Funktionerne returnerer lister og dictionaries og skriver ikke selv til konsollen, så de kan genbruges af både CLI, dashboard og plot. Top-10-listerne bygger på `grouped_counts.highestTabel` i `aggregation/`, som grupperer hændelserne pr. bruger, kilde-IP, destinationsvært og port. Konsoltabellerne bygges af `console/tables.py`.

### Malware match
Sikkerheds detection nuværende holder øje med MALWARE_SIGNATURE_MATCH og login failures. Hvis der er mange login failures, så en user authenication, og et password reset exempelvis, er det ret typisk eksempel på mistænkelig aktivitet, så programmet holder også øje med det. Disse bliver printed i terminal under tabellerne.
#### Fundet
Det er ifølge det indhenting, der er lavet, er det første brud sket på walter. Det kan ses blandet andet fordi han har flest fejl, hvor mange af den er login_failed. Derefter er der en user authenentication fra den IP, og så er det muligt gennem de ip spor den spytter ud at følge hvordan den hopper rundt, og ender med admin password. Den IP, 172.16.0.44, har en malware match, og senere en reset på admin password.


Top-10-listerne, opsummeringen af hændelser pr. time, fejlandel pr. port og de tre diagrammer vises i dashboardet:

```bash
pip install dash plotly
python main.py --dashboard
```

Dashboardet åbner på `http://127.0.0.1:8050` og har faner til logtabellen, overblikket, de tre diagrammer, fejlandel pr. port og top-10-listerne for brugere, kilde-IP'er og destinationsværter. Porten kan ændres med `--port`.

Overbliksfanen viser periode, fejlrate og antal unikke brugere og IP'er fra `user_ips.get_user_ip_summary()`. `scatter_plots.build_figures(records)` returnerer de tre figurer, `analysis.port_failure_rows()` leverer tallene til port-tabellen, og `tables.build_columns_table()` og `tables.build_top_n_table()` bygger tabellerne.

### Mappestruktur

| Mappe | Fil | Indhold |
|---|---|---|
| `aggregation/` | `grouped_counts.py` | Gruppering og optælling pr. bruger, IP, vært og port |
| | `counts.py` | Optælling pr. level, event, status og bruger |
| | `row_values.py` | Udtræk af værdier fra de grupperede rækker |
| | `user_ips.py` | Unikke brugere og IP'er pr. bruger |
| | `users.py` | Brugeren med flest loginforsøg |
| `console/` | `tables.py` | Konsolttabel af de grupperede rækker |
| `detection/` | `suspicious_accounts.py` | Regelbaseret detektion af mistænkelige konti |
| `visualization/` | `dashboard.py` | Dash-appen med faner, layout og callback til logtabellen |
| | `logview.py` | Filtrering og sortering af logtabellen |
| | `scatter_plots.py` | De tre scatter-plots og `build_figures()` |
| | `tables.py` | Plotly-tabeller: logtabel, top-10, fejlandel pr. port og tom tabel |
| root | `main.py` | Kommandolinjeflag, konsoltabeller og opstart af dashboardet |
| | `analysis.py` | Top-10, hændelser pr. time, fejlandel pr. port og dataserier til plots |
| | `parser.py`, `loader.py`, `model.py` | Indlæsning, parsning og datamodel |
| | `errors.py`, `config.py` | Fejltyper og konstanter |

### Valg af diagramtype

| Kolonnepar | Diagram | Begrundelse |
|---|---|---|
| `hour` vs. antal hændelser | Scatter med punkter | Begge akser er tal, og hver time er én måling. Søjler ville også virke, men scatter gør det muligt at aflæse enkeltpunkter og en eventuel tendens direkte. |
| `user` vs. andel fejl | Scatter, ét punkt pr. bruger, med en stiplet linje for den samlede fejlrate | Brugerne er kategorier, så punkterne er ikke forbundet. Referencelinjen gør det muligt at se, hvilke brugere der ligger over og under gennemsnittet. |
| `dest_port` vs. hændelsestype og IP-klasse | Scatter med port på x-aksen, hændelsestype på y-aksen, boblestørrelse som antal og farve som IP-klasse | Fire variabler i ét plot: port, kategori, antal og intern/ekstern. Portene står i numerisk rækkefølge med servicenavn, så aksen kan læses uden at slå portnumre op. |

## Tests

Testene ligger i `tests/` og kræver Python 3.10 eller nyere, ligesom programmet, samt `pytest` (`pytest-cov` til coverage). Kør kommandoerne fra repoets rod.

```bash
pip install pytest pytest-cov
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
