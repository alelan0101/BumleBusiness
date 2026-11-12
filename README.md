# Bumle Business – VPN-logovervågning

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

Testene dækker, `loader.py`, `parser.py` og `model.py`

```bash
python -m pytest --cov=parser --cov=model --cov-loader --cov-report=term-missing
```

`main.py` kan køre de samme tests som `pytest` ovenfor; med `--coverage` kommer rapporten med:

```bash
python main.py --run-tests
python main.py --run-tests --coverage
```

Loguddragene ligger i `tests/fixtures/`: `small_log.txt` er et gyldigt udsnit af sample-filen, og `edge_cases.txt` indeholder linjer, der skal afvises (manglende felt, ugyldig port), og linjer med edgecases (tom `msg`, citationstegn i `msg`).
