from enum import Enum


class CaseStatus(str, Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    CLOSED = "Closed"