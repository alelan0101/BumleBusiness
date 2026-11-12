from pathlib import Path

import pytest

from config import DEFAULT_LOG_PATH
from errors import BumleBusinessError, LogFileError
from loader import load_log_file


# En gyldig fil returneres som en liste af rå linjer uden ændringer.
def test_load_log_file_returns_raw_lines(small_log_path: Path, small_log_lines: list[str]):
    lines = load_log_file(small_log_path)

    assert lines == small_log_lines
    assert all(isinstance(line, str) for line in lines)


# Stien må også gives som str og ikke kun Path.
def test_load_log_file_accepts_string_path(small_log_path: Path, small_log_lines: list[str]):
    assert load_log_file(str(small_log_path)) == small_log_lines


# Standardstien i config.py peger på sample-filen med 541 linjer.
def test_load_default_log_file_reads_541_lines():
    assert len(load_log_file(DEFAULT_LOG_PATH)) == 541


# Manglende fil giver LogFileError med en læsbar besked, ikke en traceback.
# '/' her er en methode fra pathlib, til at returnerer en valid crossplatform path.
# tmp_path er en built-in pytest fixture, der giver en unik mappe for hver test.
def test_missing_file_raises_log_file_error(tmp_path: Path):
    with pytest.raises(LogFileError, match="blev ikke fundet"):
        load_log_file(tmp_path / "findes_ikke.log")


# En tom fil afvises, så programmet ikke fortsætter med 0 records.
def test_empty_file_raises_log_file_error(tmp_path: Path):
    empty_file = tmp_path / "tom.log"
    empty_file.write_text("", encoding="utf-8")

    with pytest.raises(LogFileError, match="tom"):
        load_log_file(empty_file)


# En mappe som sti afvises med en forklarende fejl.
def test_directory_raises_log_file_error(tmp_path: Path):
    with pytest.raises(LogFileError, match="mappe"):
        load_log_file(tmp_path)


# Bytes der ikke er gyldig UTF-8 giver LogFileError i stedet for crash.
def test_non_utf8_file_raises_log_file_error(tmp_path: Path):
    corrupt_file = tmp_path / "korrupt.log"
    corrupt_file.write_bytes(b"\xff\xfe\xfa") # BOM UFT-16 Little Endian encoding

    with pytest.raises(LogFileError, match="UTF-8"):
        load_log_file(corrupt_file)


# Alle load-fejl arver fra BumleBusinessError, så main.py kan fange dem samlet.
def test_log_file_error_is_bumlebusiness_error(tmp_path: Path):
    with pytest.raises(BumleBusinessError):
        load_log_file(tmp_path / "findes_ikke.log")
