# time in seconds to wait before re-requesting a page
import dataclasses
import time

CACHE_TIMEOUT = 300


@dataclasses.dataclass
class Course:
    code: int


class CourseManager:
    _instance = None

    def __init__(self):
        # each dictionary mapping courses to their status, and time since last queried
        self._courses: dict[Course, (str, int)] = {}

    def get_course(self, course_code: int):
        if time.time() - self._courses[Course(course_code)][1] > CACHE_TIMEOUT:
            pass

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
