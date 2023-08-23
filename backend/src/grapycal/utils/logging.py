import logging
import os

def setup_logging():
    logger = logging.getLogger()
    level = logging.WARNING
    #level = logging.DEBUG
    logging.basicConfig(level=level)
    ch = logging.StreamHandler()
    if (os.environ.get('DEBUG').lower() == 'true'):
        ch.setLevel(logging.DEBUG)
    ch.setFormatter(ConsoleLogFormatter())
    if (os.environ.get('DEBUG').lower() == 'true'):
        logger.setLevel(logging.DEBUG)
    logger.handlers.clear()
    logger.addHandler(ch)
    ch.addFilter(NameTranslator())

    return logger

class NameTranslator(logging.Filter):
    dictionary = {
        'objectsync.server': 'OS',
        'objectsync.sobject': 'SOBJECT',
        'chatroom.server.server': 'CHAT',
        'chatroom.topic': 'TOPIC',
        'chatroom.server.client_manager': 'CLIENT',
        
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

    def format(self, record):
        log_fmt = self.FORMATS.get(record.name.split('.')[0],self.FORMATS['default']).get(record.levelno)
        formatter = logging.Formatter(log_fmt)

        return formatter.format(record)