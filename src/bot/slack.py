from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse
from config.settings import Settings
from src.services import handle_errors, logger

import requests
import os

from datetime import datetime


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

    @handle_errors(defaultReturn=[], logPrefix="Thread by Root ")
    def get_thread_by_root_message(self, rootMessageTs: str):
        """Get thread messages by root message timestamp."""
        try:
            response = self.webClient.conversations_replies(
                channel=self.channelId, ts=rootMessageTs
            )
            return response.data.get("messages", [])
        except Exception as e:
            logger.error(f"Error getting thread by root message {rootMessageTs}: {e}")
            return []

    def get_message(self, messageTs: str):
        """Get a specific message."""
        return self._get_message_data(messageTs, "message")

    @handle_errors(defaultReturn=None, logPrefix="User Info ")
    def get_user_info(self, userId: str):
        """Get user information by user ID."""
        try:
            response = self.webClient.users_info(user=userId)
            return response.data.get("user", {})
        except Exception as e:
            logger.error(f"Error getting user info for {userId}: {e}")
            return None

    @handle_errors(defaultReturn=[], logPrefix="All Users ")
    def get_all_users(self):
        """Get all users in the workspace."""
        try:
            response = self.webClient.users_list()
            return response.data.get("members", [])
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []

    @handle_errors(defaultReturn=[], logPrefix="User Profile ")
    def get_user_profile(self, userId: str):
        """Get user profile information."""
        try:
            response = self.webClient.users_profile_get(user=userId)
            return response.data.get("profile", {})
        except Exception as e:
            logger.error(f"Error getting user profile for {userId}: {e}")
            return {}

    @handle_errors(defaultReturn=[], logPrefix="User Lookup ")
    def lookup_user_by_email(self, email: str):
        """Look up user by email address."""
        try:
            response = self.webClient.users_lookupByEmail(email=email)
            return response.data.get("user", {})
        except Exception as e:
            logger.error(f"Error looking up user by email {email}: {e}")
            return None

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
            for message in messages:
                if message.get("subtype") == "thread_broadcast":
                    continue
                allMessages.append(message)
                if message.get("thread_ts"):
                    cursor = None
                    while True:
                        replies_response = self.webClient.conversations_replies(
                            channel=self.channelId,
                            ts=message["thread_ts"],
                            cursor=cursor,
                        )
                        replies = replies_response.data.get("messages", [])
                        allMessages.extend(replies)
                        if not replies_response.data.get("has_more", False):
                            break
                        cursor = replies_response.data.get("response_metadata", {}).get(
                            "next_cursor"
                        )
                        if not cursor:
                            break

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

    @handle_errors(defaultReturn=None, logPrefix="Channel Info ")
    def get_channel_info(self):
        """Get channel information."""
        response = self.webClient.conversations_info(channel=self.channelId)
        return response.data.get("channel", {})