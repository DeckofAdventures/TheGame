"""
This logger is adapted from the DataJoint Python API logger
    in the following format: `[Hour:Min][log_level]: Content`
"""
import logging
import os

logger = logging.getLogger(__name__.split(".")[0])

log_level = os.getenv("LOG_LEVEL", "INFO").upper()

log_format = logging.Formatter("[%(asctime)s][%(levelname)-s]: %(message)s", "%M:%S")

stream_handler = logging.StreamHandler()  # default handler
stream_handler.setFormatter(log_format)

logger.setLevel(level=log_level)

logger.handlers = [stream_handler]
