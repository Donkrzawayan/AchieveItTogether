import logging
import logging.handlers
import os
import sys


def setup_logging():
    logger = logging.getLogger()
    if logger.hasHandlers():
        return

    if not os.path.exists("logs"):
        os.makedirs("logs", exist_ok=True)

    log_format = logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    logger.setLevel(logging.INFO)
    logger.addHandler(console_handler)

    file_handler = logging.handlers.RotatingFileHandler(
        filename="logs/bot.log",
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(log_format)
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)

    logging.getLogger("discord").setLevel(logging.WARNING)
    logging.getLogger("discord.http").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
