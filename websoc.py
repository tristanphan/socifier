from typing import Optional, Dict, List

import requests
from requests import Response

URL = "https://api.peterportal.org/rest/v0/schedule/soc"


def get_status(department: str, number: str) -> Optional[str]:
    params = {
        "term": "2024 Spring",
        "department": department,
        "courseNumber": number,
    }

    response: Response = requests.get(URL, params=params)
    if response.status_code != 200:
        return None

    try:
        course = response.json()["schools"][0]["departments"][0]["courses"][0]
    except IndexError:
        return None

    # Find the lecture
    lecture = list(filter(lambda s: s["sectionType"] == "Lec", course["sections"]))[0]

    return lecture["status"].lower()


def get_status_by_course_code(course_code: int) -> Optional[str]:
    result = get_statuses_by_course_codes([course_code])
    if result is None:
        return None
    else:
        return result[course_code]


def get_statuses_by_course_codes(course_codes: List[int]) -> Optional[Dict[int, str]]:
    params = {
        "term": "2024 Spring",
        "sectionCodes": ",".join(str(c) for c in course_codes),
    }

    response: Response = requests.get(URL, params=params)
    if response.status_code != 200:
        return None

    statuses = {}
    for sch in response.json()["schools"]:
        for dept in sch["departments"]:
            for courses in dept["courses"]:
                for sec in courses["sections"]:
                    print(f"{courses['deptCode']} {courses['courseNumber']}: {courses['courseTitle']} "
                          f"(Section Code: {sec['sectionCode']}) is {sec['status']}")
                    statuses[int(sec['sectionCode'])] = sec['status'].lower()

    return statuses
