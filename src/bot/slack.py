import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse
from config.settings import Settings
from src.services import handle_event

import requests
import os
from functools import wraps
from datetime import datetime

logger = logging.getLogger(__name__)


def handle_errors(defaultReturn=None, logPrefix=""):
    """
    Decorator to handle common error patterns in Slack API calls.

    Args:
        defaultReturn: Value to return on error
        logPrefix: Prefix for log messages
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"{logPrefix}Error in {func.__name__}: {e}")
                return defaultReturn

        return wrapper

    return decorator


class SlackBot:
    def __init__(self, token: str, channelId: str = ""):
        self.token = token
        self.webClient = WebClient(token=token)
        self.channelId = channelId

    @handle_errors(defaultReturn=[], logPrefix="Message Data ")
    def _get_message_data(self, messageTs: str, dataType: str):
        """
        Generic method to get message data with error handling.

        Args:
            messageTs: Message timestamp
            dataType: Type of data to extract ('reactions', 'files', etc.)

        Returns:
            List of data or empty list on error
        """
        response = self.webClient.conversations_history(
            channel=self.channelId, latest=messageTs, limit=1, inclusive=True
        )
        if response.data["messages"]:
            if dataType == "message":
                return response.data["messages"][0]
            else:
                return response.data["messages"][0].get(dataType, [])
        else:
            logger.error(
                f"No messages found for message {messageTs} in channel {self.channelId}"
            )
            return []

    def get_channel_id(self):
        """Get the channel ID."""
        return self.channelId

    def set_channel_id(self, channelId: str):
        """Set the channel ID."""
        self.channelId = channelId

    def set_token(self, token: str):
        """Set the token."""
        self.token = token
        self.webClient = WebClient(token=self.token)

    def get_reactions(self, messageTs: str):
        """Get reactions for a specific message."""
        return self._get_message_data(messageTs, "reactions")

    def get_files(self, messageTs: str):
        """Get files for a specific message."""
        return self._get_message_data(messageTs, "files")

    def get_message(self, messageTs: str):
        """Get a specific message."""
        return self._get_message_data(messageTs, "message")

    @handle_errors(defaultReturn=None, logPrefix="Get message date ")
    def get_message_date(self, messageTs: str, formatStr: str = "%Y-%m-%d %H:%M:%S"):
        """Get formatted send date of a message."""
        messageDate = datetime.fromtimestamp(float(messageTs))
        if messageDate:
            return messageDate.strftime(formatStr)
        return None

    @handle_errors(defaultReturn=[], logPrefix="History ")
    def get_all_history(self):
        """Get all message history from a channel."""
        allMessages = []
        cursor = None

        while True:
            response = self.webClient.conversations_history(
                channel=self.channelId, limit=1000, cursor=cursor
            )

            messages = response.data.get("messages", [])
            allMessages.extend(messages)

            if not response.data.get("has_more", False):
                break

            cursor = response.data.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                break

        return allMessages

    @handle_errors(defaultReturn=None, logPrefix="Download ")
    def download_file(self, fileId: str, outputPath: str = ""):
        """Download a file from Slack."""
        response = self.webClient.files_info(file=fileId)
        fileInfo = response["file"]
        fileUrl = fileInfo["url_private"]
        headers = {
            "Authorization": f"Bearer {Settings.SLACK_BOT_TOKEN}",
        }
        outputName = outputPath
        if not outputPath:
            if not os.path.exists("downloads"):
                os.makedirs("downloads")
            outputName = (
                "downloads/"
                + datetime.now().strftime("%Y%m%d%H%M%S%f")
                + "_"
                + fileInfo["name"]
            )
        with requests.get(fileUrl, headers=headers, stream=True) as r:
            r.raise_for_status()  # Raise an exception for bad status codes
            with open(outputName, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        logger.info(
            f"File '{fileId}' {fileInfo['name']} ({fileInfo['size']} bytes) downloaded successfully to '{outputName}'."
        )
        return outputName
