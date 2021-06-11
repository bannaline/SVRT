import logging
from logging import handlers


logFormatter = logging.Formatter("[%(asctime)s] %(message)s")

logHandler = handlers.TimedRotatingFileHandler(filename='debug.log', when='midnight', interval=1,
                                               backupCount=2, encoding='utf-8')
logHandler.setFormatter(logFormatter)
logHandler.suffix = "%Y%m%d"

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(logHandler)
