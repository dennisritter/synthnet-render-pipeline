""" Parses CLI Arguments """
import logging
import os
from datetime import datetime

# def init_logger(log_path):
#     logging.basicConfig(format='[%(asctime)s] %(levelname)-8s %(message)s',
#                         level=logging.INFO,
#                         datefmt='%Y-%m-%d %H:%M:%S',
#                         filename=log_path)
#     logging.basicConfig(
#         format='[%(asctime)s] %(name)s %(levelname)-8s %(message)s',
#         level=logging.DEBUG,
#         datefmt='%Y-%m-%d %H:%M:%S',
#         filename=log_path)


def init_logger(output_path: str = './output', override_handlers: bool = True):
    """Inititializes the logger.

    Args:
        output_path (str): The path where the output should be saved.
        override_handlers (bool). Whether to override existing handler
            (e.g. some a configurated in a dependecy).
    """
    # create logger
    logger = logging.getLogger()
    # override
    if override_handlers:
        if logger.hasHandlers():
            logger.handlers.clear()
    # set level
    logger.setLevel(logging.DEBUG)
    # create output dir
    if not os.path.exists(output_path):
        try:
            os.makedirs(output_path)
        except:
            logger.error("Error while try to create directory for the logger.")
    # create file handler which logs even debug messages
    now = datetime.now()
    fh = logging.FileHandler(
        os.path.join(output_path,
                     now.strftime("%Y%m%d_%H%M%S") + '.log'))
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        '{asctime} | {name} | [{levelname}] {message}',
        datefmt='%Y-%m-%d %H:%M:%S',
        style='{')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)


def separator():
    return ('#' * 20)
