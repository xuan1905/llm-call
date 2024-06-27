import logging


class LogConfig:
    def __init__(self, class_name):
        self.class_name = class_name

    def get_logger(self):
        logger = logging.getLogger(self.class_name)
        logger.setLevel(logging.INFO)
        logger.propagate = False  # to remove duplicate logs

        if logger.hasHandlers():
            logger.handlers = []
        ch = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)

        return logger
