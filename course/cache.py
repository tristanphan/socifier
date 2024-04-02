from typing import Dict, Optional

import serializer
from course.course import Course, Status
from logger import logger

COURSE_CACHE_FILEPATH = "data/course_cache.json"


class CourseCache:
    """
    Stores courses and their last known statuses
    """

    def __init__(self):
        cache = serializer.load(COURSE_CACHE_FILEPATH)

        self._cache: Dict[Course, Status] = cache or {}

    def lookup(self, course: Course) -> Optional[Status]:
        """
        :return: The last known status of the course, or None if the course is not in the cache
        """

        item = self._cache.get(course)

        if item is None:
            logger.warning(f"[CourseCache] Cache miss for {course}")
        else:
            logger.info(f"[CourseCache] Found {course}: {item} in cache")

        return item

    def update(self, course: Course, status: Status):
        """
        Replaces the current entry for the course with the new status
        """

        logger.info(f"[CourseCache] Updating {course} to {status}")

        self._cache[course] = status
        serializer.dump(self._cache, COURSE_CACHE_FILEPATH)

    _instance = None

    @classmethod
    def get_instance(cls) -> "CourseCache":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
