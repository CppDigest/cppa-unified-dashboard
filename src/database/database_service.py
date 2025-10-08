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
    async def create_user(self, userData: Dict[str, Any]) -> User:
        """Create or update a user."""
        try:
            # Extract profile data
            profile = userData.get("profile", {})

            data = {
                "id": userData["id"],
                "name": userData.get("name"),
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
                "color": userData.get("color"),
                "avatarHash": profile.get("avatar_hash"),
                "isBot": userData.get("is_bot", False),
                "isDeleted": userData.get("deleted", False),
                "isAppUser": userData.get("is_app_user", False),
                "isEmailConfirmed": userData.get("is_email_confirmed", False),
                "isAdmin": userData.get("is_admin", False),
                "isOwner": userData.get("is_owner", False),
                "isPrimaryOwner": userData.get("is_primary_owner", False),
                "isRestricted": userData.get("is_restricted", False),
                "isUltraRestricted": userData.get("is_ultra_restricted", False),
                "isCustomImage": profile.get("is_custom_image", False),
                "alwaysActive": profile.get("always_active", False),
                "whoCanShareContactCard": userData.get("who_can_share_contact_card"),
                "teamId": userData.get("team_id"),
                "timezone": userData.get("tz"),
                "timezoneLabel": userData.get("tz_label"),
                "timezoneOffset": userData.get("tz_offset"),
                "updated": (
                    datetime.fromtimestamp(userData.get("updated", 0) / 1000)
                    if userData.get("updated")
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

            existingUser = await self.prisma.user.find_unique(
                where={"id": userData["id"]}
            )
            if existingUser:
                user = await self.prisma.user.update(
                    where={"id": userData["id"]}, data=data
                )
            else:
                user = await self.prisma.user.create(data=data)

            logger.info(f"User {user.id} created/updated successfully")
            return user
        except Exception as e:
            logger.error(f"Error creating user {userData.get('id')}: {e}")

    async def get_user(self, userId: str) -> Optional[User]:
        """Get user by ID."""
        try:
            return await self.prisma.user.find_unique(where={"id": userId})
        except Exception as e:
            logger.error(f"Error getting user {userId}: {e}")
            return None

    async def get_all_users(self) -> List[User]:
        """Get all users."""
        try:
            return await self.prisma.user.find_many()
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []

    # Channel Operations
    async def create_channel(self, channelData: Dict[str, Any]) -> Channel:
        """Create or update a channel."""
        try:
            # Extract purpose and topic data
            purpose = channelData.get("purpose", {})
            topic = channelData.get("topic", {})
            
            created = datetime.fromtimestamp(channelData.get("created")) if channelData.get("created") else None
            updated = datetime.fromtimestamp(channelData.get("updated") / 1000) if channelData.get("updated") else None

            data = {
                "id": channelData["id"],
                "name": channelData.get("name", ""),
                "nameNormalized": channelData.get("name_normalized"),
                "created": created,
                "updated": updated,
                "creator": channelData.get("creator"),
                "isPrivate": channelData.get("is_private", False),
                "isArchived": channelData.get("is_archived", False),
                "isGeneral": channelData.get("is_general", False),
                "isMember": channelData.get("is_member", False),
                "isChannel": channelData.get("is_channel", False),
                "isGroup": channelData.get("is_group", False),
                "isIm": channelData.get("is_im", False),
                "isMpim": channelData.get("is_mpim", False),
                "isShared": channelData.get("is_shared", False),
                "isExtShared": channelData.get("is_ext_shared", False),
                "isOrgShared": channelData.get("is_org_shared", False),
                "isPendingExtShared": channelData.get("is_pending_ext_shared", False),
                "unlinked": channelData.get("unlinked", 0),
                "contextTeamId": channelData.get("context_team_id"),
                "sharedTeamIds": channelData.get("shared_team_ids", []),
                "pendingShared": channelData.get("pending_shared", []),
                "pendingConnectedTeamIds": channelData.get("pending_connected_team_ids", []),
                "parentConversation": channelData.get("parent_conversation"),
                "lastRead": channelData.get("last_read"),
                "topic": topic.get("value") if topic else None,
                "purpose": purpose.get("value") if purpose else None,
                "previousNames": channelData.get("previous_names", []),
            }

            existingChannel = await self.prisma.channel.find_unique(
                where={"id": channelData["id"]}
            )
            if existingChannel:
                channel = await self.prisma.channel.update(
                    where={"id": channelData["id"]}, data=data
                )
            else:
                channel = await self.prisma.channel.create(data=data)

            logger.info(f"Channel {channel.id} created/updated successfully")
            return "Channel created/updated successfully"
        except Exception as e:
            logger.error(f"Error creating channel {channelData.get('id')}: {e}")

    async def get_channel(self, channelId: str) -> Optional[Channel]:
        """Get channel by ID."""
        try:
            return await self.prisma.channel.find_unique(where={"id": channelId})
        except Exception as e:
            logger.error(f"Error getting channel {channelId}: {e}")
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
        self, messageData: Dict[str, Any], channelId: str
    ) -> Message:
        """Create or update a message."""
        try:
            # Convert timestamp to datetime
            timestamp = datetime.fromtimestamp(float(messageData["ts"]))
            data = {
                "id": messageData["ts"],
                "clientMsgId": messageData.get("client_msg_id"),
                "channelId": messageData.get("channel", channelId),
                "userId": messageData.get("user", ""),
                "text": messageData.get("text"),
                "timestamp": timestamp,
                "type": messageData.get("type", "message"),
                "subtype": messageData.get("subtype"),
                "isEdited": bool(messageData.get("edited")),
                "editedAt": (
                    messageData.get("edited", {}).get("ts")
                    if messageData.get("edited")
                    else None
                ),
                "editedBy": (
                    messageData.get("edited", {}).get("user")
                    if messageData.get("edited")
                    else None
                ),
                "threadTs": (
                    messageData.get("thread_ts")
                    if messageData.get("thread_ts", None) != messageData.get("ts")
                    else None
                ),
                "replyCount": messageData.get("reply_count", 0),
                "replyUsersCount": messageData.get("reply_users_count", 0),
                "isLocked": messageData.get("is_locked", False),
                "subscribed": messageData.get("subscribed", False),
                "botId": messageData.get("bot_id"),
                "appId": messageData.get("app_id"),
                "team": messageData.get("team"),
            }

            existingMessage = await self.prisma.message.find_unique(
                where={"id": messageData["ts"]}
            )
            if existingMessage:
                message = await self.prisma.message.update(
                    where={"id": messageData["ts"]}, data=data
                )
            else:
                message = await self.prisma.message.create(data=data)

            # Handle reactions
            if messageData.get("reactions"):
                await self._create_reactions(message.id, messageData["reactions"])

            # Handle files
            if messageData.get("files"):
                await self._create_files(
                    message.id, messageData["files"], messageData.get("user", "")
                )

            logger.info(f"Message {message.id} created/updated successfully")
            return message
        except Exception as e:
            logger.error(f"Error creating message {messageData.get('ts')}: {e}")

    async def get_message(self, messageId: str) -> Optional[Message]:
        """Get message by ID with all relations."""
        try:
            return await self.prisma.message.find_unique(
                where={"id": messageId},
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
            logger.error(f"Error getting message {messageId}: {e}")
            return None

    async def get_channel_messages(
        self, channelId: str, limit: int = 100
    ) -> List[Message]:
        """Get messages from a channel with thread structure."""
        try:
            # Get root messages (not replies)
            messages = await self.prisma.message.find_many(
                where={
                    "channelId": channelId,
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
            logger.error(f"Error getting channel messages {channelId}: {e}")
            return []

    async def get_thread_messages(self, threadTs: str) -> List[Message]:
        """Get all messages in a thread."""
        try:
            return await self.prisma.message.find_many(
                where={"threadTs": threadTs},
                include={"user": True, "reactions": True, "files": True},
                order={"timestamp": "asc"},
            )
        except Exception as e:
            logger.error(f"Error getting thread messages {threadTs}: {e}")
            return []

    # Bulk Operations
    async def bulk_create_users(self, usersData: List[Dict[str, Any]]) -> int:
        """Bulk create/update users."""
        created_count = 0
        for userData in usersData:
            try:
                await self.create_user(userData)
                created_count += 1
            except Exception as e:
                logger.error(f"Error creating user {userData.get('id')}: {e}")
        logger.info(f"Created/updated {created_count} users")
        return created_count

    async def bulk_create_messages(
        self, messagesData: List[Dict[str, Any]], channelId: str
    ) -> int:
        """Bulk create/update messages."""
        created_count = 0
        for messageData in messagesData:
            try:
                await self.create_message(messageData, channelId)
                created_count += 1
            except Exception as e:
                logger.error(f"Error creating message {messageData.get('ts')}: {e}")
        logger.info(f"Created/updated {created_count} messages")
        return created_count

    async def bulk_create_channels(self, channelsData: List[Dict[str, Any]]) -> int:
        """Bulk create/update channels."""
        created_count = 0
        for channelData in channelsData:
            try:
                await self.create_channel(channelData)
                created_count += 1
            except Exception as e:
                logger.error(f"Error creating channel {channelData.get('id')}: {e}")
        logger.info(f"Created/updated {created_count} channels")
        return created_count

    # Helper Methods
    async def _create_reactions(
        self, messageId: str, reactionsData: List[Dict[str, Any]]
    ):
        """Create reactions for a message."""
        try:
            for reactionData in reactionsData:
                data = {
                    "name": reactionData["name"],
                    "count": reactionData["count"],
                    "userId": reactionData["users"][0],
                    "messageId": messageId,
                }
                existingReaction = await self.prisma.reaction.find_unique(
                    where={
                        "messageId_userId_name": {
                            "messageId": messageId,
                            "userId": reactionData["users"][0],
                            "name": reactionData["name"],
                        }
                    }
                )
                if existingReaction:
                    await self.prisma.reaction.update(
                        where={"id": existingReaction.id}, data=data
                    )
                else:
                    await self.prisma.reaction.create(data=data)

        except Exception as e:
            logger.error(f"Error creating reactions for message {messageId}: {e}")

    async def _create_files(
        self, messageId: str, filesData: List[Dict[str, Any]], userId: str
    ):
        """Create files for a message."""
        try:
            for fileData in filesData:
                data = {
                    "slackFileId": fileData["id"],
                    "name": fileData.get("name", ""),
                    "title": fileData.get("title"),
                    "mimetype": fileData.get("mimetype"),
                    "filetype": fileData.get("filetype"),
                    "prettyType": fileData.get("pretty_type"),
                    "size": fileData.get("size"),
                    "mode": fileData.get("mode"),
                    "isExternal": fileData.get("is_external", False),
                    "externalType": fileData.get("external_type"),
                    "isPublic": fileData.get("is_public", False),
                    "publicUrlShared": fileData.get("public_url_shared", False),
                    "displayAsBot": fileData.get("display_as_bot", False),
                    "username": fileData.get("username"),
                    "urlPrivate": fileData.get("url_private"),
                    "urlPrivateDownload": fileData.get("url_private_download"),
                    "permalink": fileData.get("permalink"),
                    "permalinkPublic": fileData.get("permalink_public"),
                    "editLink": fileData.get("edit_link"),
                    "preview": fileData.get("preview"),
                    "previewHighlight": fileData.get("preview_highlight"),
                    "lines": fileData.get("lines"),
                    "linesMore": fileData.get("lines_more"),
                    "previewIsTruncated": fileData.get("preview_is_truncated", False),
                    "isStarred": fileData.get("is_starred", False),
                    "skippedShares": fileData.get("skipped_shares", False),
                    "hasRichPreview": fileData.get("has_rich_preview", False),
                    "fileAccess": fileData.get("file_access"),
                    "thumb64": fileData.get("thumb_64"),
                    "thumb80": fileData.get("thumb_80"),
                    "thumb360": fileData.get("thumb_360"),
                    "thumb360W": fileData.get("thumb_360_w"),
                    "thumb360H": fileData.get("thumb_360_h"),
                    "thumb480": fileData.get("thumb_480"),
                    "thumb480W": fileData.get("thumb_480_w"),
                    "thumb480H": fileData.get("thumb_480_h"),
                    "thumb160": fileData.get("thumb_160"),
                    "thumb720": fileData.get("thumb_720"),
                    "thumb720W": fileData.get("thumb_720_w"),
                    "thumb720H": fileData.get("thumb_720_h"),
                    "thumb800": fileData.get("thumb_800"),
                    "thumb800W": fileData.get("thumb_800_w"),
                    "thumb800H": fileData.get("thumb_800_h"),
                    "thumb960": fileData.get("thumb_960"),
                    "thumb960W": fileData.get("thumb_960_w"),
                    "thumb960H": fileData.get("thumb_960_h"),
                    "thumb1024": fileData.get("thumb_1024"),
                    "thumb1024W": fileData.get("thumb_1024_w"),
                    "thumb1024H": fileData.get("thumb_1024_h"),
                    "thumbTiny": fileData.get("thumb_tiny"),
                    "originalW": fileData.get("original_w"),
                    "originalH": fileData.get("original_h"),
                    "messageId": messageId,
                    "userId": userId,
                    "userTeam": fileData.get("user_team"),
                }
                existingFile = await self.prisma.file.find_unique(
                    where={"slackFileId": fileData["id"]}
                )
                if existingFile:
                    await self.prisma.file.update(
                        where={"id": existingFile.id}, data=data
                    )
                else:
                    await self.prisma.file.create(data=data)
        except Exception as e:
            logger.error(f"Error creating files for message {messageId}: {e}")

    # Search and Filter Operations
    async def search_messages(
        self, query: str, channelId: Optional[str] = None
    ) -> List[Message]:
        """Search messages by text content."""
        try:
            whereClause = {"text": {"contains": query, "mode": "insensitive"}}
            if channelId:
                whereClause["channelId"] = channelId

            return await self.prisma.message.find_many(
                where=whereClause,
                include={"user": True, "reactions": True, "files": True},
                order={"timestamp": "desc"},
            )
        except Exception as e:
            logger.error(f"Error searching messages: {e}")
            return []

    async def get_user_messages(self, userId: str, limit: int = 50) -> List[Message]:
        """Get messages from a specific user."""
        try:
            return await self.prisma.message.find_many(
                where={"userId": userId},
                include={"user": True, "reactions": True, "files": True},
                order={"timestamp": "desc"},
                take=limit,
            )
        except Exception as e:
            logger.error(f"Error getting user messages {userId}: {e}")
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
