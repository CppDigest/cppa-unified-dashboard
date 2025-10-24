from typing import List, Dict, Any, Optional, TYPE_CHECKING, Tuple

from src.services import logger
import json

if TYPE_CHECKING:
    from src.bot import SlackBot
    from src.database import DatabaseService


class SlackDatabaseService:
    def __init__(self, slack_bot: "SlackBot", db_service: "DatabaseService"):
        self.slack_bot = slack_bot
        self.db_service = db_service

    async def insert_channel(self, channel: Dict[str, Any]):
        """Insert a channel into the database."""
        try:
            await self.db_service.create_channel(channel)
        except Exception as e:
            logger.error(f"Error inserting channel {channel.get('id')}: {e}")

    async def sync_all_users(self):
        """Sync all users into the database."""
        try:
            users_data = self.slack_bot.get_all_users()
            await self.db_service.bulk_create_users(users_data)
        except Exception as e:
            logger.error(f"Error syncing all users: {e}")

    async def sync_all_data(self) -> Dict[str, int]:
        """Sync all Slack data to database."""
        try:
            channels = self.slack_bot.get_all_channels()
            for channel in channels:
                channel_id = channel.get("id")
                logger.info(f"Starting data sync for channel {channel_id}")

                # Set channel for bot
                self.slack_bot.set_channel_id(channel_id)

                # Get channel info
                logger.info("Fetching channel info...")
                channel_data = self.slack_bot.get_channel_info()
                channel_create_result = await self.db_service.create_channel(
                    channel_data
                )

                logger.info(f"Created channel: {channel_create_result}")

                # Get all messages
                logger.info("Fetching all messages...")
                messages_data = self.slack_bot.get_all_history()

                logger.info(f"Sync completed for channel {channel_id}")

        except Exception as e:
            logger.error(f"Error syncing data: {e}")

    async def sync_channel_messages(self, channel_id: str) -> int:
        """Sync messages from a specific channel."""
        try:
            logger.info(f"Syncing messages from channel {channel_id}")
            self.slack_bot.set_channel_id(channel_id)

            messages_data = self.slack_bot.get_all_history()
            messages_count = await self.db_service.bulk_create_messages(messages_data)

            logger.info(f"Synced {messages_count} messages from channel {channel_id}")
            return messages_count
        except Exception as e:
            logger.error(f"Error syncing channel messages {channel_id}: {e}")

    async def sync_thread_messages(self, thread_ts: str) -> int:
        """Sync messages from a specific thread."""
        try:
            logger.info(f"Syncing thread messages {thread_ts}")

            thread_messages = self.slack_bot.get_thread_by_root_message(thread_ts)
            messages_count = await self.db_service.bulk_create_messages(thread_messages)

            logger.info(f"Synced {messages_count} thread messages")
            return messages_count
        except Exception as e:
            logger.error(f"Error syncing thread messages {thread_ts}: {e}")

    async def sync_user_data(self) -> int:
        """Sync all users from workspace."""
        try:
            logger.info("Syncing all users...")

            users_data = self.slack_bot.get_all_users()
            users_count = await self.db_service.bulk_create_users(users_data)

            logger.info(f"Synced {users_count} users")
            return users_count
        except Exception as e:
            logger.error(f"Error syncing users: {e}")

    async def get_channel_messages_from_db(
        self, channel_id: str, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get messages from database with thread structure."""
        try:
            messages = await self.db_service.get_channel_messages(channel_id, limit)

            # Convert to dict format for JSON serialization
            if len(messages) == 0:
                return []
            result = []
            for message in messages:
                message_dict = {
                    "id": message.id,
                    "text": message.text,
                    "timestamp": (
                        message.timestamp.isoformat() if message.timestamp else None
                    ),
                    "type": message.type,
                    "subtype": message.subtype,
                    "isEdited": message.isEdited,
                    "editedAt": message.editedAt,
                    "editedBy": message.editedBy,
                    "threadTs": message.threadTs,
                    "replyCount": message.replyCount,
                    "user": (
                        {
                            "id": message.user.id if message.user else None,
                            "realName": message.user.realName if message.user else None,
                            "displayName": (
                                message.user.displayName if message.user else None
                            ),
                            "image48": message.user.image48 if message.user else None,
                        }
                        if message.user
                        else None
                    ),
                    "reactions": [
                        {
                            "name": reaction.name,
                            "count": reaction.count,
                            "userId": reaction.userId,
                        }
                        for reaction in message.reactions
                    ],
                    "files": [
                        {
                            "id": file.slackFileId,
                            "name": file.name,
                            "size": file.size,
                            "mimetype": file.mimetype,
                            "urlPrivate": file.urlPrivate,
                            "thumb360": file.thumb360,
                        }
                        for file in message.files
                    ],
                    "threadMessages": [
                        {
                            "id": thread_msg.id,
                            "text": thread_msg.text,
                            "timestamp": (
                                thread_msg.timestamp.isoformat()
                                if thread_msg.timestamp
                                else None
                            ),
                            "user": (
                                {
                                    "id": (
                                        thread_msg.user.id if thread_msg.user else None
                                    ),
                                    "realName": (
                                        thread_msg.user.realName
                                        if thread_msg.user
                                        else None
                                    ),
                                    "displayName": (
                                        thread_msg.user.displayName
                                        if thread_msg.user
                                        else None
                                    ),
                                }
                                if thread_msg.user
                                else None
                            ),
                            "reactions": [
                                {"name": reaction.name, "count": reaction.count}
                                for reaction in thread_msg.reactions
                            ],
                            "files": [
                                {
                                    "id": file.slackFileId,
                                    "name": file.name,
                                    "size": file.size,
                                }
                                for file in thread_msg.files
                            ],
                        }
                        for thread_msg in message.threadMessages
                    ],
                }
                result.append(message_dict)

            return result
        except Exception as e:
            logger.error(f"Error getting channel messages from DB {channel_id}: {e}")
            return []

    async def search_messages_in_db(
        self, query: str, channel_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search messages in database."""
        try:
            messages = await self.db_service.search_messages(query, channel_id)

            result = []
            for message in messages:
                message_dict = {
                    "id": message.id,
                    "text": message.text,
                    "timestamp": (
                        message.timestamp.isoformat() if message.timestamp else None
                    ),
                    "channelId": message.channelId,
                    "user": (
                        {
                            "id": message.user.id if message.user else None,
                            "realName": message.user.realName if message.user else None,
                            "displayName": (
                                message.user.displayName if message.user else None
                            ),
                        }
                        if message.user
                        else None
                    ),
                    "reactions": [
                        {"name": reaction.name, "count": reaction.count}
                        for reaction in message.reactions
                    ],
                    "files": [
                        {"id": file.slackFileId, "name": file.name, "size": file.size}
                        for file in message.files
                    ],
                }
                result.append(message_dict)

            return result
        except Exception as e:
            logger.error(f"Error searching messages in DB: {e}")
            return []

    async def get_user_messages_from_db(
        self, user_id: str, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get messages from a specific user."""
        try:
            messages = await self.db_service.get_user_messages(user_id, limit)

            result = []
            for message in messages:
                message_dict = {
                    "id": message.id,
                    "text": message.text,
                    "timestamp": (
                        message.timestamp.isoformat() if message.timestamp else None
                    ),
                    "channelId": message.channelId,
                    "user": (
                        {
                            "id": message.user.id if message.user else None,
                            "realName": message.user.realName if message.user else None,
                            "displayName": (
                                message.user.displayName if message.user else None
                            ),
                        }
                        if message.user
                        else None
                    ),
                    "reactions": [
                        {"name": reaction.name, "count": reaction.count}
                        for reaction in message.reactions
                    ],
                    "files": [
                        {"id": file.slackFileId, "name": file.name, "size": file.size}
                        for file in message.files
                    ],
                }
                result.append(message_dict)

            return result
        except Exception as e:
            logger.error(f"Error getting user messages from DB {user_id}: {e}")
            return []

    async def get_thread_messages_from_db(self, thread_ts: str) -> List[Dict[str, Any]]:
        """Get thread messages from database."""
        try:
            messages = await self.db_service.get_thread_messages(thread_ts)

            result = []
            for message in messages:
                message_dict = {
                    "id": message.id,
                    "text": message.text,
                    "timestamp": (
                        message.timestamp.isoformat() if message.timestamp else None
                    ),
                    "user": (
                        {
                            "id": message.user.id if message.user else None,
                            "realName": message.user.realName if message.user else None,
                            "displayName": (
                                message.user.displayName if message.user else None
                            ),
                        }
                        if message.user
                        else None
                    ),
                    "reactions": [
                        {"name": reaction.name, "count": reaction.count}
                        for reaction in message.reactions
                    ],
                    "files": [
                        {"id": file.slackFileId, "name": file.name, "size": file.size}
                        for file in message.files
                    ],
                }
                result.append(message_dict)

            return result
        except Exception as e:
            logger.error(f"Error getting thread messages from DB {thread_ts}: {e}")
            return []

    async def get_direct_messages(self) -> Tuple[int, int]:
        """Get direct messages from database."""
        try:
            dm_channels = self.slack_bot.get_direct_channels()
            msg_count = 0
            for channel in dm_channels:
                self.slack_bot.set_channel_id(channel.get("id"))
                channel_data = self.slack_bot.get_channel_info()
                await self.db_service.create_channel(channel_data)
                history = self.slack_bot.get_all_history()

                result = await self.db_service.bulk_create_messages(
                    history, channel_data.get("id")
                )
                msg_count += result
            return len(dm_channels), msg_count

        except Exception as e:
            logger.error(f"Error getting direct messages from DB: {e}")
            return []
