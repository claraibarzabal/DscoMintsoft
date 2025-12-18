import logging
import os
from logging.handlers import RotatingFileHandler

# -------------------------------------------------
# Configuración
# -------------------------------------------------
LOG_DIR = "logs"
LOG_FILE = "products.log"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

MAX_BYTES = 10 * 1024 * 1024  # 10 MB
BACKUP_COUNT = 5


# -------------------------------------------------
# Setup
# -------------------------------------------------
def _ensure_log_dir():
    os.makedirs(LOG_DIR, exist_ok=True)


def get_product_logger():
    _ensure_log_dir()

    logger = logging.getLogger("product_sync")
    logger.setLevel(LOG_LEVEL)

    # Evita handlers duplicados
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | product | %(message)s"
    )

    # -----------------------------
    # Archivo (con rotación)
    # -----------------------------
    file_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, LOG_FILE),
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    # -----------------------------
    # Consola
    # -----------------------------
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger
