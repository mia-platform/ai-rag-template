import logging
import os
import socket
import sys
import time

from pythonjsonlogger import jsonlogger


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def process_log_record(self, log_record):
        # Rename levelno to level
        log_record["level"] = log_record.pop("levelno")
        # Rename message to msg
        log_record["msg"] = log_record.pop("message")
        # Rename asctime to time and convert it to milliseconds
        log_record["time"] = int(time.time() * 1000)
        # Add pid
        log_record["pid"] = os.getpid()
        # Add hostname
        log_record["hostname"] = socket.gethostname()
        return super().process_log_record(log_record)


def get_logger(logger_name="mialogger"):
    # Clear any existing handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logger = logging.getLogger(logger_name)

    # Set up root logger
    logging.root.setLevel(os.environ.get("LOG_LEVEL", logging.INFO))
    logger.setLevel(os.environ.get("LOG_LEVEL", logging.INFO))

    # Use custom JSON formatter
    formatter = CustomJsonFormatter(
        fmt="%(levelno)s %(message)s",
    )

    # Create a new handler with a filter
    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(lambda record: record.name.startswith(logger_name))
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.propagate = False

    return logger
