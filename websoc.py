from typing import Optional, Dict, List

import requests
from requests import Response

from course import Course, Status
from datatypes import SectionCode
from logger import logger

URL = "https://api.peterportal.org/rest/v0/schedule/soc"


def get_course_statuses(codes: List[SectionCode]) -> Optional[Dict[Course, Status]]:
    params = {
        "term": "2024 Spring",
        "sectionCodes": ",".join(map(str, codes))
    }
    response: Response = requests.get(URL, params=params)
    content = response.json()

    logger.info(f"[WebSoc] Requested {codes} and got {response.status_code}")

    if response.status_code != 200:
        # Bad response
        return None

    courses: Dict[Course, Status] = {}
    for school_json in content["schools"]:
        for department_json in school_json["departments"]:
            for course_json in department_json["courses"]:
                for section_json in course_json["sections"]:
                    # Collect course
                    course = Course(
                        code=int(section_json["sectionCode"]),
                        department=course_json["deptCode"],
                        number=course_json["courseNumber"],
                        title=course_json["courseTitle"],
                    )
                    logger.info(f"[WebSoc] Found course {course}")

                    # Collect status
                    status = section_json["status"].lower()

                    courses[course] = Status(status)

    return courses
