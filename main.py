import os

from bot import DiscordBot
from logger import set_up_pycord_logger, set_up_socifier_logger

if __name__ == "__main__":
    # Make sure the data folder exists
    if not os.path.exists("./data"):
        os.makedirs("./data")

    # Make sure the data folder exists
    if not os.path.exists("./logs"):
        os.makedirs("./logs")

    # Set up loggers
    set_up_pycord_logger()
    set_up_socifier_logger()

    DiscordBot.initialize()
