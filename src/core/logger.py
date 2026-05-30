import os
import logging

from logging.handlers import RotatingFileHandler

from pythonjsonlogger import jsonlogger

from src.core.config import settings


os.makedirs("logs", exist_ok=True)


def get_logger(
    logger_name: str
) -> logging.Logger:

    logger = logging.getLogger(
        logger_name
    )

    if logger.handlers:
        return logger

    logger.setLevel(
        settings.LOG_LEVEL
    )

    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s"
    )

    file_handler = RotatingFileHandler(
        filename="logs/app.log",
        maxBytes=1024 * 1024,
        backupCount=5
    )

    file_handler.setFormatter(
        formatter
    )

    console_handler = logging.StreamHandler()

    console_handler.setFormatter(
        formatter
    )

    logger.addHandler(
        file_handler
    )

    logger.addHandler(
        console_handler
    )

    logger.propagate = False

    return logger