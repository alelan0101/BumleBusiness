import sys
from pathlib import Path

import pytest

# Gør repoets rod importerbar, så testene kan importere loader, parser og model.
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


# To små loguddrag: et gyldigt udsnit og et med kanttilfælde.
@pytest.fixture
def small_log_path() -> Path:
    return FIXTURES_DIR / "small_log.txt"


@pytest.fixture
def edge_cases_path() -> Path:
    return FIXTURES_DIR / "edge_cases.txt"


@pytest.fixture
def small_log_lines(small_log_path: Path) -> list[str]:
    return small_log_path.read_text(encoding="utf-8").splitlines()


@pytest.fixture
def edge_case_lines(edge_cases_path: Path) -> list[str]:
    return edge_cases_path.read_text(encoding="utf-8").splitlines()
