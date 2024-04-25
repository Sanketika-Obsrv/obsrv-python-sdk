from logging import getLogger
from obsrv.models import ErrorData

logger = getLogger(__name__)

class ObsrvException(Exception):
    def __init__(self, error):
        self.error = error
        super().__init__(self.error.error_msg)

# class UnsupportedDataFormatException(ObsrvException):
#     def __init__(self, data_format):
#         super().__init__(ErrorData("DATA_FORMAT_ERR", f"Unsupported data format {data_format}"))