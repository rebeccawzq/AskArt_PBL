import logging
import os
import sys

from loguru import logger
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()
chat_client = OpenAI()
img_client = OpenAI()
follow_up_client = OpenAI()


class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def unify_logging():
    logging.root.handlers = [InterceptHandler()]
    logging.getLogger('uvicorn.access').setLevel(os.getenv('UVICORN_LEVEL', 'ERROR'))

    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    logger.configure(handlers=[{'sink': sys.stdout}])
