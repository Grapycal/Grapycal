import logging
import os

from objectsync import EventTopic

def setup_logging():
    logger = logging.getLogger()
    level = logging.INFO
    #level = logging.DEBUG
    logging.basicConfig(level=level)
    ch = logging.StreamHandler()
    if os.environ.get('DEBUG') is not None and (os.environ.get('DEBUG').lower() == 'true'):
        ch.setLevel(logging.DEBUG)
    ch.setFormatter(ConsoleLogFormatter())
    if os.environ.get('DEBUG') is not None and (os.environ.get('DEBUG').lower() == 'true'):
        logger.setLevel(logging.DEBUG)
    logger.handlers.clear()
    logger.addHandler(ch)
    ch.addFilter(NameTranslator())

    to_frontend_handler = LogToFrontendHandler()
    to_frontend_handler.setLevel(logging.INFO)
    to_frontend_handler.addFilter(NameTranslator())
    to_frontend_handler.setFormatter(FrontendFormatter())
    logger.addHandler(to_frontend_handler)

    return logger

class NameTranslator(logging.Filter):
    dictionary = {
        'objectsync.server': 'OS',
        'objectsync.sobject': 'SOBJECT',
        'topicsync.server.server': 'TOPICSYNC',
        'topicsync.topic': 'TOPIC',
        'topicsync.server.client_manager': 'CLIENT',
        'workspace': 'WORKSPACE',
        'grapycal.extension.extensionManager': 'EXTENSION',
    }
    def filter(self, record):
        if record.name.startswith('websockets'):
            return False
        record.short_name = self.dictionary.get(record.name,record.name)
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
    #format = "%(threadName)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    format_ = f"%(levelname)5s {bold}[%(short_name)s]\t{no_bold} %(message)s"

    FORMATS = {
        'default':{
            logging.DEBUG: blue + format_ + reset,
            logging.INFO: grey + format_ + reset,
            logging.WARNING: yellow + format_ + reset,
            logging.ERROR: red + format_ + reset,
            logging.CRITICAL: bold_red + format_ + reset
        },
        'objectsync':{
            logging.DEBUG: green + format_ + reset,
            logging.INFO: grey + format_ + reset,
            logging.WARNING: yellow + format_ + reset,
            logging.ERROR: red + format_ + reset,
            logging.CRITICAL: bold_red + format_ + reset
        },
    }

    def format(self, record: logging.LogRecord):
        log_fmt = self.FORMATS.get(record.name.split('.')[0],self.FORMATS['default']).get(record.levelno)
        formatter = logging.Formatter(log_fmt)

        return formatter.format(record)
    
class FrontendFormatter(logging.Formatter):
    time_format = "%H:%M:%S"
    format_ = fmt='%(asctime)s\t%(message)s'

    def format(self, record: logging.LogRecord):
        formatter = logging.Formatter(self.format_, datefmt=self.time_format)
        return formatter.format(record)

frontend_message_topic:None|EventTopic = None

class LogToFrontendHandler(logging.Handler):
    def emit(self, record: logging.LogRecord):
        global frontend_message_topic
        if frontend_message_topic is None:
            return
        frontend_message_topic.emit(message=self.format(record))