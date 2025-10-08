from typing import List, Dict, Any, Optional, TYPE_CHECKING

from src.services import logger
import json

if TYPE_CHECKING:
    from src.bot import SlackBot
    from src.database import DatabaseService


class SlackDatabaseService:
    def __init__(self, slackBot: "SlackBot", dbService: "DatabaseService"):
        self.slackBot = slackBot
        self.dbService = dbService

    async def sync_all_data(self, channelId: str) -> Dict[str, int]:
        """Sync all Slack data to database."""
        try:
            logger.info(f"Starting data sync for channel {channelId}")

            # Set channel for bot
            self.slackBot.set_channel_id(channelId)
            
            # Get all users
            logger.info("Fetching all users...")
            usersData = self.slackBot.get_all_users()
            usersCount = await self.dbService.bulk_create_users(usersData)
            
            # Get channel info
            logger.info("Fetching channel info...")
            channelData = self.slackBot.get_channel_info()
            channelCreateResult = await self.dbService.create_channel(channelData)
            
            logger.info(f"Created channel: {channelCreateResult}")

            # Get all messages
            logger.info("Fetching all messages...")
            messagesData = self.slackBot.get_all_history()
            messagesCount = await self.dbService.bulk_create_messages(
                messagesData, channelId
            )

            logger.info(f"Sync completed: {usersCount} users, {messagesCount} messages")
            return {"users": usersCount, "messages": messagesCount}
        except Exception as e:
            logger.error(f"Error syncing data: {e}")

    async def sync_channel_messages(self, channelId: str) -> int:
        """Sync messages from a specific channel."""
        try:
            logger.info(f"Syncing messages from channel {channelId}")
            self.slackBot.set_channel_id(channelId)

            messagesData = self.slackBot.get_all_history()
            messagesCount = await self.dbService.bulk_create_messages(messagesData)

            logger.info(f"Synced {messagesCount} messages from channel {channelId}")
            return messagesCount
        except Exception as e:
            logger.error(f"Error syncing channel messages {channelId}: {e}")

    async def sync_thread_messages(self, threadTs: str) -> int:
        """Sync messages from a specific thread."""
        try:
            logger.info(f"Syncing thread messages {threadTs}")

            threadMessages = self.slackBot.get_thread_by_root_message(threadTs)
            messagesCount = await self.dbService.bulk_create_messages(threadMessages)

            logger.info(f"Synced {messagesCount} thread messages")
            return messagesCount
        except Exception as e:
            logger.error(f"Error syncing thread messages {threadTs}: {e}")

    async def sync_user_data(self) -> int:
        """Sync all users from workspace."""
        try:
            logger.info("Syncing all users...")

            usersData = self.slackBot.get_all_users()
            usersCount = await self.dbService.bulk_create_users(usersData)

            logger.info(f"Synced {usersCount} users")
            return usersCount
        except Exception as e:
            logger.error(f"Error syncing users: {e}")

    async def get_channel_messages_from_db(
        self, channelId: str, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get messages from database with thread structure."""
        try:
            messages = await self.dbService.get_channel_messages(channelId, limit)

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
            logger.error(f"Error getting channel messages from DB {channelId}: {e}")
            return []

    async def search_messages_in_db(
        self, query: str, channelId: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search messages in database."""
        try:
            messages = await self.dbService.search_messages(query, channelId)

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
        self, userId: str, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get messages from a specific user."""
        try:
            messages = await self.dbService.get_user_messages(userId, limit)

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
            logger.error(f"Error getting user messages from DB {userId}: {e}")
            return []

    async def get_thread_messages_from_db(self, threadTs: str) -> List[Dict[str, Any]]:
        """Get thread messages from database."""
        try:
            messages = await self.dbService.get_thread_messages(threadTs)

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
            logger.error(f"Error getting thread messages from DB {threadTs}: {e}")
            return []
