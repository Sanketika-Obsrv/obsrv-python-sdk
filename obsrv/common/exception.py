# from obsrv.models import ErrorData
from obsrv.utils import LoggerController

logger = LoggerController(__name__)


class ObsrvException(Exception):
    def __init__(self, error):
        self.error = error
        super().__init__(self.error.error_msg)
        logger.exception(
            f"exception called from {self.__class__.__name__} with error {self.error.error_code} - {self.error.error_msg}"
        )


# class UnsupportedDataFormatException(ObsrvException):
#     def __init__(self, data_format):
#         super().__init__(ErrorData("DATA_FORMAT_ERR", f"Unsupported data format {data_format}"))
