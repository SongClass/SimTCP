"""
Code for getting and configuring a logger for project.
"""

import logging
import sys


def get_logger(log_name: str) -> logging.Logger:
    """Returns a logging instance, configured so that all non-filtered messages
    are sent to STDOUT.
    """
    logger = logging.getLogger(log_name)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(name)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
