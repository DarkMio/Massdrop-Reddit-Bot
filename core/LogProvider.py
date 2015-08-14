import logging
import time
import sys


FORMAT = '%(asctime)s [%(levelname)s] -- [%(name)s:%(module)s/%(funcName)s]-- %(message)s'
CHAT_FORMAT = '[%(asctime)] %(message)'
LOGGING_LEVELS = {"NOTSET": logging.NOTSET, "DEBUG": logging.DEBUG,
                  "INFO": logging.INFO, "WARNING": logging.WARNING,
                  "ERROR": logging.ERROR, "CRITICAL": logging.CRITICAL}
TIME_FORMAT = '%H:%M:%S'


class SingleLevelFilter(logging.Filter):
    """Filters a certain logging-level out - used to split error messages to stderr instead of writing into stdout."""
    def __init__(self, passlevel, reject):
        self.passlevel = passlevel
        self.reject = reject

    def filter(self, record):
        if self.reject:
            return (record.levelno != self.passlevel)
        else:
            return (record.levelno == self.passlevel)


def setup_logging(log_level="INFO", console_log_level=None):
    """Thanks to Renol: https://github.com/RenolY2/Renol-IRC-rv2
       This logging handler is quite powerful and nicely formatted."""
    null_handler = logging.NullHandler()
    logging.basicConfig(level=log_level, handlers=[null_handler])

    if console_log_level is None:
        console_log_level = log_level

    log_level = LOGGING_LEVELS[log_level]
    console_log_level = LOGGING_LEVELS[console_log_level]

    logging_format = logging.Formatter(FORMAT, datefmt=TIME_FORMAT)


    # Set up the handler for logging to console
    filter_info = SingleLevelFilter(logging.INFO, True)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_log_level)
    console_handler.setFormatter(logging_format)
    console_handler.addFilter(filter_info)

    # Separating error and regular output
    not_filter_info = SingleLevelFilter(logging.INFO, False)
    standard_handler = logging.StreamHandler(sys.__stdout__)
    standard_handler.setLevel(console_log_level)
    standard_handler.setFormatter(logging_format)
    standard_handler.addFilter(not_filter_info)

    # this logger writes completely into the console.
    bot_logger = logging.getLogger("bot")
    bot_logger.propagate = False
    bot_logger.addHandler(console_handler)
    bot_logger.addHandler(standard_handler)

    plugin_logger = logging.getLogger("plugin")
    plugin_logger.propagate = False
    plugin_logger.addHandler(console_handler)
    plugin_logger.addHandler(standard_handler)

    database_logger = logging.getLogger("database")
    database_logger.propagate = False
    database_logger.addHandler(console_handler)
    database_logger.addHandler(standard_handler)

    bot_logger.info("MassdropBot Logger initialized.")
    logging.getLogger("requests").setLevel(logging.WARNING)

    offset, tzname = local_time_offset()
    if offset >= 0:
        offset = "+"+str(offset)
    else:
        offset = str(offset)

    bot_logger.info("All time stamps are in UTC{0} ({1})".format(offset, tzname))
    return bot_logger


def local_time_offset():
    """Returns UTC offset and name of time zone at current time
       Based on http://stackoverflow.com/a/13406277"""
    t = time.time()

    if time.localtime(t).tm_isdst and time.daylight:
        return -time.altzone/3600, time.tzname[1]
    else:
        return -time.timezone/3600, time.tzname[0]


if __name__ == "__main__":
    setup_logging()