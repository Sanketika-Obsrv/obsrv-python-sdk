import operator
from functools import reduce

import yaml

from .logger import LoggerController

logger = LoggerController(__name__)


class Config:
    def __init__(self, config_file_path):
        with open(config_file_path) as config_file:
            self.config = yaml.safe_load(config_file)

    def find(self, path, default=None):
        try:
            element_value = reduce(operator.getitem, path.split("."), self.config)
            return element_value
        except KeyError:
            logger.exception("key `%s` not found in config", path)
            return default
