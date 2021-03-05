from enum import Enum


class ErrorCode(Enum):
    NoError = 0
    UnknownError = 1000
    InvalidProduct = 1001
