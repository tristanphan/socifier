import dataclasses
from enum import StrEnum
from typing import Optional

from datatypes import CourseNumber, Department, SectionCode


class Status(StrEnum):
    new_only = "newonly"
    open = "open"
    waitlist = "waitl"
    full = "full"


@dataclasses.dataclass(frozen=True)
class Course:
    code: SectionCode
    department: Optional[Department] = None
    number: Optional[CourseNumber] = None
    title: Optional[str] = None

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.code == other.code

    def __hash__(self):
        return hash(self.code)
