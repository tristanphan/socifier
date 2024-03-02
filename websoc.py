from typing import List, Dict

import requests
from requests import Response

from types import Class

URL = "https://api.peterportal.org/rest/v0/schedule/soc"


def get_status(department: str, numbers: List[str]) -> Dict[Class, str]:
    params = {
        "term": "2024 Spring",
        "department": department,
        "courseNumber": ",".join(numbers),
    }

    response: Response = requests.get(URL, params=params)
    if response.status_code != 200:
        return {}

    try:
        course = response.json()["schools"][0]["departments"][0]["courses"][0]
    except IndexError:
        return {}

    # Find the lecture
    lecture = list(filter(lambda s: s["sectionType"] == "Lec", course["sections"]))[0]

    return lecture["status"].lower()
