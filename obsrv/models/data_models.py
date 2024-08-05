from dataclasses import dataclass
from enum import Enum

# from typing import Optional, Dict, Any


class EventID(Enum):
    LOG = "LOG"
    METRIC = "METRIC"


class StatusCode(Enum):
    SUCCESS = "success"
    FAILED = "failed"


@dataclass
class ErrorData:
    error_code: str
    error_msg: str


# @dataclass
# class ContextData:
#     connector_id: str
#     dataset_id: str
#     connector_instance_id: str
#     connector_type: str
#     data_format: str

# @dataclass
# class ErrorLog:
#     pdata_id: str
#     pdata_status: StatusCode
#     error_type: str
#     error_code: str
#     error_message: str
#     error_count: Optional[int] = None

# @dataclass
# class EData:
#     error: Optional[ErrorLog] = None
#     extra: Optional[Dict[str, Any]] = None

# @dataclass
# class SystemEvent:
#     etype: EventID
#     ctx: ContextData
#     data: EData
#     ets: int
