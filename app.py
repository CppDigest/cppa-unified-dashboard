import threading
import logging
import json

from src.bot import SlackBot
from config.settings import Settings

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    token = Settings.SLACK_BOT_TOKEN
    slackBot = SlackBot(token=token)
    print("fetch <channelId> - Fetch all messages from a channel")
    print("exit - Exit the program")

    while True:
        userInput = input(">> ").strip()
        if (
            userInput.lower() == "exit"
            or userInput.lower() == "q"
            or userInput.lower() == "quit"
        ):
            break
        elif userInput.startswith("fetch"):
            _, channelId = userInput.split()
            slackBot.set_channel_id(channelId)
            res = slackBot.get_all_history()
            print(res)
        else:
            print("Invalid command")
