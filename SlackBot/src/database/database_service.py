from datetime import datetime
from typing import List, Dict, Optional, Any
from prisma import Prisma
from prisma.models import Message, User, Reaction, File, Channel

from src.services import logger


class DatabaseService:
    def __init__(self):
        self.prisma = Prisma()

    async def connect(self):
        """Connect to the database."""
        await self.prisma.connect()
        logger.info("Connected to PostgreSQL database")

    async def disconnect(self):
        """Disconnect from the database."""
        await self.prisma.disconnect()
        logger.info("Disconnected from PostgreSQL database")

    # User Operations
    async def create_user(self, user_data: Dict[str, Any]) -> User:
        """Create or update a user."""
        try:
            # Extract profile data
            profile = user_data.get("profile", {})

            data = {
                "id": user_data["id"],
                "name": user_data.get("name"),
                "email": profile.get("email"),
                "realName": profile.get("real_name"),
                "displayName": profile.get("display_name"),
                "realNameNormalized": profile.get("real_name_normalized"),
                "displayNameNormalized": profile.get("display_name_normalized"),
                "firstName": profile.get("first_name"),
                "lastName": profile.get("last_name"),
                "title": profile.get("title"),
                "phone": profile.get("phone"),
                "skype": profile.get("skype"),
                "color": user_data.get("color"),
                "avatarHash": profile.get("avatar_hash"),
                "isBot": user_data.get("is_bot", False),
                "isDeleted": user_data.get("deleted", False),
                "isAppUser": user_data.get("is_app_user", False),
                "isEmailConfirmed": user_data.get("is_email_confirmed", False),
                "isAdmin": user_data.get("is_admin", False),
                "isOwner": user_data.get("is_owner", False),
                "isPrimaryOwner": user_data.get("is_primary_owner", False),
                "isRestricted": user_data.get("is_restricted", False),
                "isUltraRestricted": user_data.get("is_ultra_restricted", False),
                "isCustomImage": profile.get("is_custom_image", False),
                "alwaysActive": profile.get("always_active", False),
                "whoCanShareContactCard": user_data.get("who_can_share_contact_card"),
                "teamId": user_data.get("team_id"),
                "timezone": user_data.get("tz"),
                "timezoneLabel": user_data.get("tz_label"),
                "timezoneOffset": user_data.get("tz_offset"),
                "updated": (
                    datetime.fromtimestamp(user_data.get("updated", 0) / 1000)
                    if user_data.get("updated")
                    else None
                ),
                "image24": profile.get("image_24"),
                "image32": profile.get("image_32"),
                "image48": profile.get("image_48"),
                "image72": profile.get("image_72"),
                "image192": profile.get("image_192"),
                "image512": profile.get("image_512"),
                "image1024": profile.get("image_1024"),
                "imageOriginal": profile.get("image_original"),
                "statusText": profile.get("status_text"),
                "statusTextCanonical": profile.get("status_text_canonical"),
                "statusEmoji": profile.get("status_emoji"),
                "statusExpiration": profile.get("status_expiration"),
                "botId": profile.get("bot_id"),
                "apiAppId": profile.get("api_app_id"),
            }

            existing_user = await self.prisma.user.find_unique(
                where={"id": user_data["id"]}
            )
            if existing_user:
                user = await self.prisma.user.update(
                    where={"id": user_data["id"]}, data=data
                )
            else:
                user = await self.prisma.user.create(data=data)

            logger.info(f"User {user.id} created/updated successfully")
            return user
        except Exception as e:
            logger.error(f"Error creating user {user_data.get('id')}: {e}")

    async def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        try:
            return await self.prisma.user.find_unique(where={"id": user_id})
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None

    async def get_all_users(self) -> List[User]:
        """Get all users."""
        try:
            return await self.prisma.user.find_many()
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []

    # Channel Operations
    async def create_channel(self, channel_data: Dict[str, Any]) -> Channel:
        """Create or update a channel."""
        try:
            # Extract purpose and topic data
            purpose = channel_data.get("purpose", {})
            topic = channel_data.get("topic", {})

            created = (
                datetime.fromtimestamp(channel_data.get("created"))
                if channel_data.get("created")
                else None
            )
            updated = (
                datetime.fromtimestamp(channel_data.get("updated") / 1000)
                if channel_data.get("updated")
                else None
            )

            data = {
                "id": channel_data["id"],
                "name": channel_data.get("name", ""),
                "nameNormalized": channel_data.get("name_normalized"),
                "created": created,
                "updated": updated,
                "creator": channel_data.get("creator"),
                "isPrivate": channel_data.get("is_private", False),
                "isArchived": channel_data.get("is_archived", False),
                "isGeneral": channel_data.get("is_general", False),
                "isMember": channel_data.get("is_member", False),
                "isChannel": channel_data.get("is_channel", False),
                "isGroup": channel_data.get("is_group", False),
                "isIm": channel_data.get("is_im", False),
                "isMpim": channel_data.get("is_mpim", False),
                "isShared": channel_data.get("is_shared", False),
                "isExtShared": channel_data.get("is_ext_shared", False),
                "isOrgShared": channel_data.get("is_org_shared", False),
                "isPendingExtShared": channel_data.get("is_pending_ext_shared", False),
                "unlinked": channel_data.get("unlinked", 0),
                "contextTeamId": channel_data.get("context_team_id"),
                "sharedTeamIds": channel_data.get("shared_team_ids", []),
                "pendingShared": channel_data.get("pending_shared", []),
                "pendingConnectedTeamIds": channel_data.get(
                    "pending_connected_team_ids", []
                ),
                "parentConversation": channel_data.get("parent_conversation"),
                "lastRead": channel_data.get("last_read"),
                "topic": topic.get("value") if topic else None,
                "purpose": purpose.get("value") if purpose else None,
                "previousNames": channel_data.get("previous_names", []),
            }

            existing_channel = await self.prisma.channel.find_unique(
                where={"id": channel_data["id"]}
            )
            if existing_channel:
                channel = await self.prisma.channel.update(
                    where={"id": channel_data["id"]}, data=data
                )
            else:
                channel = await self.prisma.channel.create(data=data)

            logger.info(f"Channel {channel.id} created/updated successfully")
            return "Channel created/updated successfully"
        except Exception as e:
            logger.error(f"Error creating channel {channel_data.get('id')}: {e}")

    async def get_channel(self, channel_id: str) -> Optional[Channel]:
        """Get channel by ID."""
        try:
            return await self.prisma.channel.find_unique(where={"id": channel_id})
        except Exception as e:
            logger.error(f"Error getting channel {channel_id}: {e}")
            return None

    async def get_all_channels(self) -> List[Channel]:
        """Get all channels."""
        try:
            return await self.prisma.channel.find_many()
        except Exception as e:
            logger.error(f"Error getting all channels: {e}")
            return []

    # Message Operations
    async def create_message(
        self, message_data: Dict[str, Any], channel_id: str
    ) -> Message:
        """Create or update a message."""
        try:
            # Convert timestamp to datetime
            timestamp = datetime.fromtimestamp(float(message_data["ts"]))
            data = {
                "id": message_data["ts"],
                "clientMsgId": message_data.get("client_msg_id"),
                "channelId": message_data.get("channel", channel_id),
                "userId": message_data.get("user", ""),
                "text": message_data.get("text"),
                "timestamp": timestamp,
                "type": message_data.get("type", "message"),
                "subtype": message_data.get("subtype"),
                "isEdited": bool(message_data.get("edited")),
                "editedAt": (
                    message_data.get("edited", {}).get("ts")
                    if message_data.get("edited")
                    else None
                ),
                "editedBy": (
                    message_data.get("edited", {}).get("user")
                    if message_data.get("edited")
                    else None
                ),
                "threadTs": (
                    message_data.get("thread_ts")
                    if message_data.get("thread_ts", None) != message_data.get("ts")
                    else None
                ),
                "replyCount": message_data.get("reply_count", 0),
                "replyUsersCount": message_data.get("reply_users_count", 0),
                "isLocked": message_data.get("is_locked", False),
                "subscribed": message_data.get("subscribed", False),
                "botId": message_data.get("bot_id"),
                "appId": message_data.get("app_id"),
                "team": message_data.get("team"),
                "isEmbed": False,
            }

            existing_message = await self.prisma.message.find_unique(
                where={"id": message_data["ts"]}
            )
            if existing_message:
                message = await self.prisma.message.update(
                    where={"id": message_data["ts"]}, data=data
                )
            else:
                message = await self.prisma.message.create(data=data)

            # Handle reactions
            if message_data.get("reactions"):
                await self._create_reactions(message.id, message_data["reactions"])

            # Handle files
            if message_data.get("files"):
                await self._create_files(
                    message.id, message_data["files"], message_data.get("user", "")
                )

            logger.info(f"Message {message.id} created/updated successfully")
            return message
        except Exception as e:
            logger.error(f"Error creating message {message_data.get('ts')}: {e}")

    async def update_message(self, message_id: str, message_data: Dict[str, Any]):
        """Update a message."""
        try:
            return await self.prisma.message.update(
                where={"id": message_id}, data=message_data
            )
        except Exception as e:
            logger.error(f"Error updating message {message_id}: {e}")
            return None

    async def get_message(self, message_id: str) -> Optional[Message]:
        """Get message by ID with all relations."""
        try:
            return await self.prisma.message.find_unique(
                where={"id": message_id},
                include={
                    "user": True,
                    "reactions": True,
                    "files": True,
                    "threadMessages": {
                        "include": {"user": True, "reactions": True, "files": True},
                        "orderBy": {"timestamp": "asc"},
                    },
                    "parentMessage": True,
                },
            )
        except Exception as e:
            logger.error(f"Error getting message {message_id}: {e}")
            return None

    async def get_messages_for_rag(
        self, skip: int = 0, take: int = 100
    ) -> List[Message]:
        """Get messages for RAG with all relations."""
        try:
            return await self.prisma.message.find_many(
                skip=skip,
                take=take,
                where={
                    "isEmbed": False,
                    "AND": [{"subtype": None}, {"subtype": "thread_broadcast"}],
                },
                include={
                    "channel": True,
                    "user": True,
                },
                order={"timestamp": "desc"},
            )
        except Exception as e:
            logger.error(f"Error getting messages for RAG: {e}")
            return []

    async def delete_message(self, message_id: str):
        """Delete a message."""
        try:
            await self.prisma.message.update(
                where={"id": message_id}, data={"isDeleted": True, "isEmbed": True}
            )
        except Exception as e:
            logger.error(f"Error deleting message {message_id}: {e}")

    async def get_channel_messages(
        self, channel_id: str, limit: int = 100
    ) -> List[Message]:
        """Get messages from a channel with thread structure."""
        try:
            # Get root messages (not replies)
            messages = await self.prisma.message.find_many(
                where={
                    "channelId": channel_id,
                    "OR": [
                        {"threadTs": None},
                        {"subtype": "thread_broadcast"},
                    ],
                },
                include={
                    "user": True,
                    "reactions": True,
                    "files": True,
                    "threadMessages": {
                        "include": {"user": True, "reactions": True, "files": True},
                        "orderBy": {"timestamp": "asc"},
                    },
                },
                order={"timestamp": "desc"},
                take=limit,
            )
            return messages
        except Exception as e:
            logger.error(f"Error getting channel messages {channel_id}: {e}")
            return []

    async def get_thread_messages(self, thread_ts: str) -> List[Message]:
        """Get all messages in a thread."""
        try:
            return await self.prisma.message.find_many(
                where={"threadTs": thread_ts},
                include={"user": True, "reactions": True, "files": True},
                order={"timestamp": "asc"},
            )
        except Exception as e:
            logger.error(f"Error getting thread messages {thread_ts}: {e}")
            return []

    # Bulk Operations
    async def bulk_create_users(self, users_data: List[Dict[str, Any]]) -> int:
        """Bulk create/update users."""
        created_count = 0
        for user_data in users_data:
            try:
                await self.create_user(user_data)
                created_count += 1
            except Exception as e:
                logger.error(f"Error creating user {user_data.get('id')}: {e}")
        logger.info(f"Created/updated {created_count} users")
        return created_count

    async def bulk_create_messages(
        self, messages_data: List[Dict[str, Any]], channel_id: str
    ) -> int:
        """Bulk create/update messages."""
        created_count = 0
        for message_data in messages_data:
            try:
                await self.create_message(message_data, channel_id)
                created_count += 1
            except Exception as e:
                logger.error(f"Error creating message {message_data.get('ts')}: {e}")
        logger.info(f"Created/updated {created_count} messages")
        return created_count

    async def bulk_create_channels(self, channels_data: List[Dict[str, Any]]) -> int:
        """Bulk create/update channels."""
        created_count = 0
        for channel_data in channels_data:
            try:
                await self.create_channel(channel_data)
                created_count += 1
            except Exception as e:
                logger.error(f"Error creating channel {channel_data.get('id')}: {e}")
        logger.info(f"Created/updated {created_count} channels")
        return created_count

    # Helper Methods
    async def _create_reactions(
        self, message_id: str, reactions_data: List[Dict[str, Any]]
    ):
        """Create reactions for a message."""
        try:
            for reaction_data in reactions_data:
                for user in reaction_data["users"]:
                    data = {
                        "name": reaction_data["name"],
                        "userId": user,
                        "messageId": message_id,
                    }
                    existing_reaction = await self.prisma.reaction.find_unique(
                        where={
                            "messageId_userId_name": {
                                "messageId": message_id,
                                "userId": user,
                                "name": reaction_data["name"],
                            }
                        }
                    )
                    if existing_reaction:
                        continue
                    else:
                        await self.prisma.reaction.create(data=data)

        except Exception as e:
            logger.error(f"Error creating reactions for message {message_id}: {e}")

    async def _delete_reactions(
        self, message_id: str, reactions_data: List[Dict[str, Any]]
    ):
        """Delete reactions for a message."""
        try:
            for reaction_data in reactions_data:
                for user in reaction_data["users"]:
                    await self.prisma.reaction.delete(
                        where={
                            "messageId_userId_name": {
                                "messageId": message_id,
                                "userId": user,
                                "name": reaction_data["name"],
                            }
                        }
                    )

        except Exception as e:
            logger.error(f"Error deleting reactions for message {message_id}: {e}")

    async def _create_files(
        self, message_id: str, files_data: List[Dict[str, Any]], user_id: str
    ):
        """Create files for a message."""
        try:
            for file_data in files_data:
                data = {
                    "slackFileId": file_data["id"],
                    "name": file_data.get("name", ""),
                    "title": file_data.get("title"),
                    "mimetype": file_data.get("mimetype"),
                    "filetype": file_data.get("filetype"),
                    "prettyType": file_data.get("pretty_type"),
                    "size": file_data.get("size"),
                    "mode": file_data.get("mode"),
                    "isExternal": file_data.get("is_external", False),
                    "externalType": file_data.get("external_type"),
                    "isPublic": file_data.get("is_public", False),
                    "publicUrlShared": file_data.get("public_url_shared", False),
                    "displayAsBot": file_data.get("display_as_bot", False),
                    "username": file_data.get("username"),
                    "urlPrivate": file_data.get("url_private"),
                    "urlPrivateDownload": file_data.get("url_private_download"),
                    "permalink": file_data.get("permalink"),
                    "permalinkPublic": file_data.get("permalink_public"),
                    "editLink": file_data.get("edit_link"),
                    "preview": file_data.get("preview"),
                    "previewHighlight": file_data.get("preview_highlight"),
                    "lines": file_data.get("lines"),
                    "linesMore": file_data.get("lines_more"),
                    "previewIsTruncated": file_data.get("preview_is_truncated", False),
                    "isStarred": file_data.get("is_starred", False),
                    "skippedShares": file_data.get("skipped_shares", False),
                    "hasRichPreview": file_data.get("has_rich_preview", False),
                    "fileAccess": file_data.get("file_access"),
                    "thumb64": file_data.get("thumb_64"),
                    "thumb80": file_data.get("thumb_80"),
                    "thumb360": file_data.get("thumb_360"),
                    "thumb360W": file_data.get("thumb_360_w"),
                    "thumb360H": file_data.get("thumb_360_h"),
                    "thumb480": file_data.get("thumb_480"),
                    "thumb480W": file_data.get("thumb_480_w"),
                    "thumb480H": file_data.get("thumb_480_h"),
                    "thumb160": file_data.get("thumb_160"),
                    "thumb720": file_data.get("thumb_720"),
                    "thumb720W": file_data.get("thumb_720_w"),
                    "thumb720H": file_data.get("thumb_720_h"),
                    "thumb800": file_data.get("thumb_800"),
                    "thumb800W": file_data.get("thumb_800_w"),
                    "thumb800H": file_data.get("thumb_800_h"),
                    "thumb960": file_data.get("thumb_960"),
                    "thumb960W": file_data.get("thumb_960_w"),
                    "thumb960H": file_data.get("thumb_960_h"),
                    "thumb1024": file_data.get("thumb_1024"),
                    "thumb1024W": file_data.get("thumb_1024_w"),
                    "thumb1024H": file_data.get("thumb_1024_h"),
                    "thumbTiny": file_data.get("thumb_tiny"),
                    "originalW": file_data.get("original_w"),
                    "originalH": file_data.get("original_h"),
                    "messageId": message_id,
                    "userId": user_id,
                    "userTeam": file_data.get("user_team"),
                }
                existing_file = await self.prisma.file.find_unique(
                    where={"slackFileId": file_data["id"]}
                )
                if existing_file:
                    await self.prisma.file.update(
                        where={"id": existing_file.id}, data=data
                    )
                else:
                    await self.prisma.file.create(data=data)
        except Exception as e:
            logger.error(f"Error creating files for message {message_id}: {e}")

    # Search and Filter Operations
    async def search_messages(
        self, query: str, channel_id: Optional[str] = None
    ) -> List[Message]:
        """Search messages by text content."""
        try:
            where_clause = {"text": {"contains": query, "mode": "insensitive"}}
            if channel_id:
                where_clause["channelId"] = channel_id

            return await self.prisma.message.find_many(
                where=where_clause,
                include={"user": True, "reactions": True, "files": True},
                order={"timestamp": "desc"},
            )
        except Exception as e:
            logger.error(f"Error searching messages: {e}")
            return []

    async def get_user_messages(self, user_id: str, limit: int = 50) -> List[Message]:
        """Get messages from a specific user."""
        try:
            return await self.prisma.message.find_many(
                where={"userId": user_id},
                include={"user": True, "reactions": True, "files": True},
                order={"timestamp": "desc"},
                take=limit,
            )
        except Exception as e:
            logger.error(f"Error getting user messages {user_id}: {e}")
            return []

    async def get_distinct_channel_ids(self) -> List[str]:
        """Get all distinct channel IDs from messages."""
        try:
            messages = await self.prisma.message.find_many(
                select={"channelId": True}, distinct=["channelId"]
            )
            return [msg["channelId"] for msg in messages]
        except Exception as e:
            logger.error(f"Error getting distinct channel IDs: {e}")
            return []
