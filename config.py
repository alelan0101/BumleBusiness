from pathlib import Path

APP_NAME = "Bumle Business"
APP_VERSION = "0.1.0"

BASE_DIR: Path = Path(__file__).resolve().parent

DEFAULT_LOG_PATH: Path = BASE_DIR / "cyber_security_log_sample.txt"

LOG_ENCODING = "utf-8"

LOG_COLUMNS = (
    "timestamp",
    "level",
    "event",
    "user",
    "src_ip",
    "dest_host",
    "dest_port",
    "status",
    "msg",
)

COLUMN_WIDTHS = {
    "timestamp": 19,
    "level": 7,
    "event": 22,
    "user": 10,
    "src_ip": 15,
    "dest_host": 9,
    "dest_port": 9,
    "status": 7,
    "msg": 40,
}

SUS_DETECTION = {
    "ALERT": 4,
    "MALWARE_SIGNATURE_MATCH": 2,
    
}