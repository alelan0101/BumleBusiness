
from pathlib import Path

from config import DEFAULT_LOG_PATH, LOG_ENCODING
from errors import LogFileError


def load_log_file(path: str | Path = DEFAULT_LOG_PATH) -> list[str]:
    file_path = Path(path).expanduser()

    if not file_path.exists():
        raise LogFileError(f"Logfilen blev ikke fundet: {file_path}")
    if file_path.is_dir():
        raise LogFileError(f"Stien er en mappe og ikke en fil: {file_path}")

    try:
        with file_path.open("r", encoding=LOG_ENCODING) as log_file:
            lines = log_file.read().splitlines()
    except PermissionError:
        raise LogFileError(f"Ingen læserettighed til filen: {file_path}") from None
    except UnicodeDecodeError as error:
        raise LogFileError(
            f"Filen er ikke gyldig {LOG_ENCODING.upper()}: {file_path} ({error.reason})"
        ) from None
    except OSError as error:
        raise LogFileError(
            f"Filen kunne ikke læses: {file_path} ({error.strerror})"
        ) from None

    if not lines:
        raise LogFileError(f"Logfilen er tom: {file_path}")

    return lines
