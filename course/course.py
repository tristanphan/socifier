import dataclasses
from enum import Enum
from typing import Optional

from discord import Colour

from datatypes import CourseNumber, Department, SectionCode


class Status(Enum):
    new_only = ("newonly", "New Only", Colour.blue())
    open = ("open", "Open", Colour.green())
    waitlist = ("waitl", "Waitlist", Colour.orange())
    full = ("full", "Full", Colour.red())

    def __new__(cls, value, display, color):
        obj = object.__new__(cls)
        obj._value_ = value
        obj._display = display
        obj._color = color
        return obj

    def __str__(self):
        return self._display

    def color(self):
        return self._color


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

    def __str__(self):
        return f"{self.department} {self.number} ({self.code})"
