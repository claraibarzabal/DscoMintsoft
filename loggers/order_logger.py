import logging
import os
from logging.handlers import RotatingFileHandler

# -------------------------------------------------
# Configuración global
# -------------------------------------------------
LOG_DIR = os.getenv("LOG_DIR", "logs")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", 10 * 1024 * 1024))  # 10MB
LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", 5))


def _ensure_log_dir():
    os.makedirs(LOG_DIR, exist_ok=True)


def get_logger(name: str, filename: str) -> logging.Logger:
    """
    Devuelve un logger configurado con:
    - Rotación de archivos
    - Console output
    - Nivel configurable por ENV
    """

    _ensure_log_dir()

    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    # -----------------------------
    # File handler con rotación
    # -----------------------------
    file_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, filename),
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    # -----------------------------
    # Console handler
    # -----------------------------
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger
