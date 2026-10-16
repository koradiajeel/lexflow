"""Who can see which cases.

- Owner and Staff: every case in their own firm.
- Lawyer: only cases assigned to their own lawyer profile (the lawyer whose
  `user_id` is this login). A Lawyer login that isn't linked to a lawyer
  profile sees no cases.

A case's firm comes from its lawyer. Anything a user may not see is treated
as not existing (the routes answer 404), so its existence isn't revealed.
"""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.case import Case
from app.models.enums import UserRole
from app.models.lawyer import Lawyer
from app.models.user import User


def sees_only_own_cases(user: User) -> bool:
    return user.role == UserRole.LAWYER


def user_can_see_case(db: Session, case: Case, user: User) -> bool:
    lawyer = db.scalar(select(Lawyer).where(Lawyer.id == case.lawyer_id))
    if lawyer is None or lawyer.law_firm_id != user.law_firm_id:
        return False
    if sees_only_own_cases(user):
        return lawyer.user_id == user.id
    return True
