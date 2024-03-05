from typing import Optional

import jsonpickle


def dump(obj, filepath):
    """
    Dump a jsonpickle object to a filepath
    """

    data = jsonpickle.encode(obj, keys=True)
    with open(filepath, "w") as f:
        f.write(data)


def load(filepath) -> Optional[object]:
    """
    Load a jsonpickle object from filepath
    May return an invalid object, not practical to check for that though
    """

    try:
        with open(filepath, "r") as f:
            obj = jsonpickle.decode(f.read(), keys=True)
    except FileNotFoundError:
        print(f"Couldn't load json file specified by the path: {filepath}")
        return None

    return obj