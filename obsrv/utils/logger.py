import logging
from sys import stdout


class LoggerController(logging.Logger):
    def __init__(self, name):
        super().__init__(name)

        log_format = "%(asctime)s - %(levelname)s - %(message)s"
        formatter = logging.Formatter(log_format)

        console_handler = logging.StreamHandler(stdout)
        console_handler.setFormatter(formatter)

        self.addHandler(console_handler)
        self.setLevel(logging.INFO)

    def handle(self, record):
        super().handle(record)
