from typing import Dict, Optional

from course.course import Course, Status
import serializer

COURSE_CACHE_FILEPATH = "data/course_cache.json"


class CourseCache:
    """
    Stores courses and their last known statuses
    """

    def __init__(self):
        cache = serializer.load(COURSE_CACHE_FILEPATH)
        
        # TODO it is probably a good idea to keep track of the staleness of courses in the cache
        # example case: a class is in the cache, but is no longer updated because no user is subscribed to it
        self._cache: Dict[Course, Status] = cache or {}

    def lookup(self, course: Course) -> Optional[Status]:
        """
        :return: The last known status of the course, or None if the course is not in the cache
        """
        return self._cache.get(course)

    def update(self, course: Course, status: Status):
        """
        Replaces the current entry for the course with the new status
        """
        self._cache[course] = status

        serializer.dump(self._cache, COURSE_CACHE_FILEPATH)

    _instance = None

    @classmethod
    def get_instance(cls) -> "CourseCache":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
