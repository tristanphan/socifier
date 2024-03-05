import os

from bot import DiscordBot

if __name__ == "__main__":
    # make sure the data folder exists since it isn't tracked 
    if not os.path.exists("./data"): 
        os.makedirs("./data") 

    DiscordBot.initialize()
