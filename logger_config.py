# logger_config.py

import logging
import sys

def setup_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    # Evita duplicación si ya hay handlers
    if logger.hasHandlers():
        logger.handlers.clear()
        logger.addHandler(handler)

    return logger