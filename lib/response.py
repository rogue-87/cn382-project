from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


class Status(Enum):
    SUCCESS = 1
    FAIL = 2


@dataclass
class Response:
    status: Status
    message: str
    data: Optional[Any] = None

    def to_dict(self):
        return {
            "status": self.status.name,
            "message": self.message,
            "data": self.data,
        }
