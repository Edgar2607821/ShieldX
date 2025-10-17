import logging
from shieldx import config


from shieldx.log import Log


SHIELDX_DEBUG = config.SHIELDX_DEBUG
SHIELDX_LOG_PATH = config.SHIELDX_LOG_PATH
#SHIELDX_LOG_PATH = os.environ.get("SHIELDX_LOG_PATH", "/log")


def console_handler_filter(lr: logging.LogRecord):
    if SHIELDX_DEBUG:
        return True
    return lr.levelno in (logging.INFO, logging.ERROR, logging.WARNING)


def get_logger(name: str):
    return Log(
        name                   = name,
        console_handler_filter = console_handler_filter,
        path                   = SHIELDX_LOG_PATH
    )

# Logger genérico
L = get_logger("shieldx")
