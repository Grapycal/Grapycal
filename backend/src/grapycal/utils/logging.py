import logging
import os
from typing import Callable

if 1 + 1 == 3:
    from grapycal.sobjects.node import Node

user_logger = logging.getLogger("user")


def info_extension(node: "Node|str", msg: str, *args, **kwargs):
    if isinstance(node, str):
        name = node
    else:
        name = node.get_type_name().split(".")[0]
    logging.getLogger(name).info(msg, *args, **kwargs)


def debug_extension(node: "Node|str", msg: str, *args, **kwargs):
    if isinstance(node, str):
        name = node
    else:
        name = node.get_type_name().split(".")[0]
    logging.getLogger(name).debug(msg, *args, **kwargs)


def error_extension(node: "Node|str", msg: str, *args, **kwargs):
    if isinstance(node, str):
        name = node
    else:
        name = node.get_type_name().split(".")[0]
    logging.getLogger(name).error(msg, *args, **kwargs)


def warn_extension(node: "Node|str", msg: str, *args, **kwargs):
    if isinstance(node, str):
        name = node
    else:
        name = node.get_type_name().split(".")[0]
    logging.getLogger(name).warning(msg, *args, **kwargs)


def is_env_true(name: str) -> bool:
    return os.environ.get(name) is not None and os.environ.get(name).lower() == "true"


def setup_logging():
    logging.getLogger("matplotlib").setLevel(logging.ERROR)
    logger = logging.getLogger()
    level = logging.INFO
    # level = logging.DEBUG
    logging.basicConfig(level=level)
    ch = logging.StreamHandler()
    if is_env_true("DEBUG"):
        ch.setLevel(logging.DEBUG)
    ch.setFormatter(ConsoleLogFormatter())

    debug_objectsync = False
    if is_env_true("DEBUGO"):
        logger.setLevel(logging.DEBUG)
        debug_objectsync = True
    elif is_env_true("DEBUG"):
        logger.setLevel(logging.DEBUG)

    logger.handlers.clear()
    logger.addHandler(ch)
    ch.addFilter(NameTranslator(debug_objectsync))
    ch.addFilter(DuplicateFilter())

    to_frontend_handler = LogToFrontendHandler()
    to_frontend_handler.setLevel(logging.INFO)
    to_frontend_handler.addFilter(NameTranslator(debug_objectsync))
    to_frontend_handler.addFilter(DuplicateFilter())
    to_frontend_handler.setFormatter(FrontendFormatter())
    logger.addHandler(to_frontend_handler)

    return logger


class NameTranslator(logging.Filter):
    def __init__(self, debug_objectsync: bool = False):
        self.debug_objectsync = debug_objectsync

    dictionary = {
        "objectsync.server": "objsync",
        "objectsync.sobject": "sobject",
        "topicsync.server.server": "topicsync",
        "topicsync.topic": "topic",
        "topicsync.server.client_manager": "client",
        "workspace": "workspace",
        "grapycal.extension.extensionManager": "ext_manager",
    }

    def filter(self, record):
        if record.name.startswith("websockets"):
            return False
        if (
            not self.debug_objectsync
            and (
                record.name.startswith("topicsync")
                or record.name.startswith("objectsync")
            )
            and record.levelno <= logging.DEBUG
        ):
            return False
        if record.name.startswith("grapycal_"):
            record.short_name = "ext:" + record.name[9:]
        else:
            record.short_name = self.dictionary.get(record.name, record.name)
        return True


class DuplicateFilter(logging.Filter):
    """
    filter with key of the record message
    """

    def __init__(self):
        self.record_keys = set()

    def filter(self, record):
        if not hasattr(record, "key"):
            return True
        if record.key in self.record_keys:
            return False
        self.record_keys.add(record.key)
        return True


class ConsoleLogFormatter(logging.Formatter):
    green = "\x1b[32;20m"
    blue = "\x1b[34;20m"
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    bold = "\x1b[1m"
    no_bold = "\x1b[22m"
    reset = "\x1b[0m"
    # format = "%(threadName)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    format_ = f"{bold}%(short_name)13s |{no_bold} %(message)s"

    FORMATS = {
        "default": {
            logging.DEBUG: blue + format_ + reset,
            logging.INFO: grey + format_ + reset,
            logging.WARNING: yellow + format_ + reset,
            logging.ERROR: red + format_ + reset,
            logging.CRITICAL: bold_red + format_ + reset,
        },
        "objectsync": {
            logging.DEBUG: green + format_ + reset,
            logging.INFO: grey + format_ + reset,
            logging.WARNING: yellow + format_ + reset,
            logging.ERROR: red + format_ + reset,
            logging.CRITICAL: bold_red + format_ + reset,
        },
    }

    def format(self, record: logging.LogRecord):
        log_fmt = self.FORMATS.get(
            record.name.split(".")[0], self.FORMATS["default"]
        ).get(record.levelno)
        formatter = logging.Formatter(log_fmt)

        return formatter.format(record)


class FrontendFormatter(logging.Formatter):
    time_format = "%H:%M:%S"
    format_ = fmt = "%(asctime)s\t%(message)s"

    def format(self, record: logging.LogRecord):
        formatter = logging.Formatter(self.format_, datefmt=self.time_format)
        return formatter.format(record)


send_client_msg: None | Callable[[str, str], None] = None


class LogToFrontendHandler(logging.Handler):
    def emit(self, record: logging.LogRecord):
        from grapycal.core.workspace import ClientMsgTypes

        if send_client_msg is None:
            return
        try:
            send_client_msg(self.format(record), ClientMsgTypes.STATUS)
        except:
            print("failed to send")
