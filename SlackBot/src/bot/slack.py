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
    def __init__(self, token: str, channel_id: str = ""):
        self.token = token
        self.web_client = WebClient(token=token)
        self.channel_id = channel_id

    @handle_errors(default_return=[], log_prefix="Message Data ")
    def _get_message_data(self, message_ts: str, data_type: str):
        """
        Generic method to get message data with error handling.

        Args:
            message_ts: Message timestamp
            data_type: Type of data to extract ('reactions', 'files', etc.)

        Returns:
            List of data or empty list on error
        """
        response = self.web_client.conversations_history(
            channel=self.channel_id, latest=message_ts, limit=1, inclusive=True
        )
        if response.data["messages"]:
            if data_type == "message":
                return response.data["messages"][0]
            else:
                return response.data["messages"][0].get(data_type, [])
        else:
            logger.error(
                f"No messages found for message {message_ts} in channel {self.channel_id}"
            )
            return []

    def get_channel_id(self):
        """Get the channel ID."""
        return self.channel_id

    def set_channel_id(self, channel_id: str):
        """Set the channel ID."""
        self.channel_id = channel_id

    def set_token(self, token: str):
        """Set the token."""
        self.token = token
        self.web_client = WebClient(token=self.token)

    def get_reactions(self, message_ts: str):
        """Get reactions for a specific message."""
        return self._get_message_data(message_ts, "reactions")

    def get_files(self, message_ts: str):
        """Get files for a specific message."""
        return self._get_message_data(message_ts, "files")

    @handle_errors(default_return=[], log_prefix="Thread by Root ")
    def get_thread_by_root_message(self, root_message_ts: str):
        """Get thread messages by root message timestamp."""
        try:
            response = self.web_client.conversations_replies(
                channel=self.channel_id, ts=root_message_ts
            )
            return response.data.get("messages", [])
        except Exception as e:
            logger.error(f"Error getting thread by root message {root_message_ts}: {e}")
            return []

    def get_message(self, message_ts: str):
        """Get a specific message."""
        return self._get_message_data(message_ts, "message")

    @handle_errors(default_return=None, log_prefix="User Info ")
    def get_user_info(self, user_id: str):
        """Get user information by user ID."""
        try:
            response = self.web_client.users_info(user=user_id)
            return response.data.get("user", {})
        except Exception as e:
            logger.error(f"Error getting user info for {user_id}: {e}")
            return None

    @handle_errors(default_return=[], log_prefix="All Users ")
    def get_all_users(self):
        """Get all users in the workspace."""
        try:
            response = self.web_client.users_list()
            return response.data.get("members", [])
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []

    @handle_errors(default_return=[], log_prefix="User Profile ")
    def get_user_profile(self, user_id: str):
        """Get user profile information."""
        try:
            response = self.web_client.users_profile_get(user=user_id)
            return response.data.get("profile", {})
        except Exception as e:
            logger.error(f"Error getting user profile for {user_id}: {e}")
            return {}

    @handle_errors(default_return=[], log_prefix="User Lookup ")
    def lookup_user_by_email(self, email: str):
        """Look up user by email address."""
        try:
            response = self.web_client.users_lookupByEmail(email=email)
            return response.data.get("user", {})
        except Exception as e:
            logger.error(f"Error looking up user by email {email}: {e}")
            return None

    @handle_errors(default_return=None, log_prefix="Get message date ")
    def get_message_date(self, message_ts: str, format_str: str = "%Y-%m-%d %H:%M:%S"):
        """Get formatted send date of a message."""
        message_date = datetime.fromtimestamp(float(message_ts))
        if message_date:
            return message_date.strftime(format_str)
        return None

    @handle_errors(default_return=[], log_prefix="History ")
    def get_all_history(self):
        """Get all message history from a channel."""
        all_messages = []
        cursor = None

        while True:
            response = self.web_client.conversations_history(
                channel=self.channel_id, limit=1000, cursor=cursor
            )

            messages = response.data.get("messages", [])
            for message in messages:
                if message.get("subtype") == "thread_broadcast":
                    continue
                all_messages.append(message)
                if message.get("thread_ts"):
                    cursor = None
                    while True:
                        replies_response = self.web_client.conversations_replies(
                            channel=self.channel_id,
                            ts=message["thread_ts"],
                            cursor=cursor,
                        )
                        replies = replies_response.data.get("messages", [])
                        all_messages.extend(replies)
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

        return all_messages

    @handle_errors(default_return=None, log_prefix="Download ")
    def download_file(self, file_id: str, output_path: str = ""):
        """Download a file from Slack."""
        response = self.web_client.files_info(file=file_id)
        file_info = response["file"]
        file_url = file_info["url_private"]
        headers = {
            "Authorization": f"Bearer {Settings.SLACK_BOT_TOKEN}",
        }
        output_name = output_path
        if not output_path:
            if not os.path.exists("downloads"):
                os.makedirs("downloads")
            output_name = (
                "downloads/"
                + datetime.now().strftime("%Y%m%d%H%M%S%f")
                + "_"
                + file_info["name"]
            )
        with requests.get(file_url, headers=headers, stream=True) as r:
            r.raise_for_status()  # Raise an exception for bad status codes
            with open(output_name, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        logger.info(
            f"File '{file_id}' {file_info['name']} ({file_info['size']} bytes) downloaded successfully to '{output_name}'."
        )
        return output_name

    @handle_errors(default_return=None, log_prefix="Channel Info ")
    def get_channel_info(self):
        """Get channel information."""
        response = self.web_client.conversations_info(channel=self.channel_id)
        return response.data.get("channel", {})

    @handle_errors(default_return=[], log_prefix="All Channels ")
    def get_all_channels(self):
        """Get all channels in the workspace."""
        try:
            public_channels = self.get_all_channels(types="public_channel")
            direct_channels = self.get_all_channels(types="im")
            group_direct_channels = self.get_all_channels(types="mpim")
            return public_channels + direct_channels + group_direct_channels
        except Exception as e:
            logger.error(f"Error getting all channels: {e}")
            return []

    def get_direct_channels(self):
        """Get all direct channels in the workspace."""
        try:
            response = self.web_client.conversations_list(types="im")
            return response.data.get("channels", [])
        except Exception as e:
            logger.error(f"Error getting all direct channels: {e}")
            return []

    @handle_errors(default_return=[], log_prefix="Public Channels ")
    def get_all_channels(self, types: str = "public_channel"):
        """Get all public channels in the workspace."""
        all_channels = []
        cursor = None
        while True:
            response = self.web_client.conversations_list(cursor=cursor, types=types)
            channels = response.data.get("channels", [])
            all_channels.extend(channels)
            if not response.data.get("has_more", False):
                break
            cursor = response.data.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                break
        return all_channels
