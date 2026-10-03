from enum import Enum


class CaseStatus(str, Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    CLOSED = "Closed"

class UserRole(str, Enum):
    OWNER = "Owner"
    LAWYER = "Lawyer"
    STAFF = "Staff"