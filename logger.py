import hashlib
import logging
import uuid
from logging.handlers import TimedRotatingFileHandler

logger = logging.getLogger("socifier")


def set_up_pycord_logger():
    pycord_logger = logging.getLogger("discord")
    file_handler = TimedRotatingFileHandler(
        filename="logs/discord.log",
        when="D",
        interval=1,
        backupCount=30,
        encoding="utf-8",
    )
    file_handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s"))
    pycord_logger.addHandler(file_handler)

    pycord_logger.info("*" * 40)


def set_up_socifier_logger():
    logger.setLevel(logging.INFO)
    file_handler = TimedRotatingFileHandler(
        filename="logs/socifier.log",
        when="D",
        interval=1,
        backupCount=30,
        encoding="utf-8",
    )
    file_handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s"))
    logger.addHandler(file_handler)

    logger.info("*" * 40)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s"))
    logger.addHandler(console_handler)


def obfuscate(obj, digits=4) -> str:
    """
    Obfuscate an object by hashing it and returning the last `digits` characters
    Useful for generating unique but not easily reversible anonymous identifiers
    Pass in `None` to get a random hash
    """

    # Get random hash for None
    if obj is None:
        obj = uuid.uuid4().hex

    # Convert to bytes
    obj_bytes = str(obj).encode("utf-8")
    hashed = hashlib.sha256(obj_bytes)
    digest: str = hashed.hexdigest()
    return digest[-digits:]
