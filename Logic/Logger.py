import logging
from .settings import *
import sys

formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s',
                              '%m-%d-%Y %H:%M:%S')

stderr_logger = logging.getLogger('toStderr')
stderr_handler = logging.StreamHandler(sys.stderr)
stderr_handler.setFormatter(formatter)
stderr_logger.addHandler(stderr_handler)
stderr_handler.setLevel(int(ENGINE_LOG_LOGGER_LEVEL))

file_logger = logging.getLogger('toFile')
output_file_handler = logging.FileHandler(os.path.join(ENGINE_LOG_DESTINATION, ENGINE_LOG_FILENAME))
output_file_handler.setFormatter(formatter)
file_logger.addHandler(output_file_handler)
file_logger.setLevel(int(ENGINE_LOG_LOGGER_LEVEL))


def info(message):
    ENGINE_LOG_TO_FILE and file_logger.info(message)
    ENGINE_LOG_TO_STDERR and stderr_logger.info(u"\u001b[32m" + message + u"\u001b[0m")


def debug(message):
    ENGINE_LOG_TO_FILE and file_logger.debug(message)
    ENGINE_LOG_TO_STDERR and stderr_logger.debug(u"\u001b[35m" + message + u"\u001b[0m")


def warning(message):
    ENGINE_LOG_TO_FILE and file_logger.warning(message)
    ENGINE_LOG_TO_STDERR and stderr_logger.warning(u"\u001b[33m" + message + u"\u001b[0m")
