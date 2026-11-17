
from pathlib import Path

from config import DEFAULT_LOG_PATH, LOG_ENCODING
from errors import LogFileError


# Læser hele logfilen og returnerer den som en liste af tekstlinjer, som
# parser.py bagefter kan dele op i felter.
# Alle fejl oversættes til LogFileError, så main.py kan vise en forståelig
# besked i stedet for et traceback.
def load_log_file(path: str | Path = DEFAULT_LOG_PATH) -> list[str]:
    file_path = Path(path).expanduser()

    # Tjek stien før vi prøver at åbne den, så fejlbeskeden bliver præcis
    if not file_path.exists():
        raise LogFileError(f"Logfilen blev ikke fundet: {file_path}")
    if file_path.is_dir():
        raise LogFileError(f"Stien er en mappe og ikke en fil: {file_path}")

    try:
        # splitlines() giver en streng pr. linje, uden linjeskiftet til sidst
        with file_path.open("r", encoding=LOG_ENCODING) as log_file:
            lines = log_file.read().splitlines()
    # Hver except fanger en bestemt slags fejl og laver den om til LogFileError
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

    # Python læser gerne en tom fil, men programmet har ingen data at vise
    if not lines:
        raise LogFileError(f"Logfilen er tom: {file_path}")

    return lines
