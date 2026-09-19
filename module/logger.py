# module/logger.py
import logging
import sys
from pathlib import Path

# Tentukan path absolut ke folder root proyek
BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "api.log"

logger = logging.getLogger("academic_api")
logger.setLevel(logging.INFO)

# Bersihkan handler lama agar tidak duplikat saat reload
if logger.hasHandlers():
    logger.handlers.clear()

# Handler Terminal (Konsol)
console_handler = logging.StreamHandler(sys.stdout)
console_formatter = logging.Formatter(
    "[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# Handler File (Menulis langsung ke logs/api.log)
file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8", mode="a")
file_formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

logger.propagate = False
