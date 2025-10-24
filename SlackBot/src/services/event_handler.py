from src.database import DatabaseService
from src.services import logger

from slack_sdk import WebClient

import json


async def handle_event(event: dict, client: WebClient):

    database_service = DatabaseService()
    await database_service.connect()
    event_type = event.get("type")

    with open("ref/event.json", "w") as f:
        json.dump(event, f)

    if event_type == "message":
        if event.get("channel_type") == "im":
            user = event.get("user")
            text = event.get("text")
            channel = event.get("channel")
            ts = event.get("ts")
            channel_data = client.conversations_info(channel=channel)
            await database_service.create_channel(channel_data.get("channel"))
            await database_service.create_message(event, channel)
            logger.info(f"[{channel}] {user}: {text} ({ts})")

        elif event.get("channel_type") == "mpim":
            user = event.get("user")
            text = event.get("text")
            channel = event.get("channel_id")
            ts = event.get("ts")
            channel_data = client.conversations_info(channel=channel)
            await database_service.create_channel(channel_data.get("channel"))
            await database_service.create_message(event, channel)
            logger.info(f"[{channel}] {user}: {text} ({ts})")

        elif "subtype" not in event:
            user = event.get("user")
            text = event.get("text")
            channel = event.get("channel")
            ts = event.get("ts")
            await database_service.create_message(event, channel)
            logger.info(f"[{channel}] {user}: {text} ({ts})")

        elif event.get("subtype") == "message_deleted":
            previous_message = event.get("previous_message")
            await database_service.delete_message(previous_message.get("ts"))
            logger.info(f"Message deleted: {previous_message.get("ts")}")

        elif event.get("subtype") == "message_changed":
            message = event.get("message")
            message_data = {
                "isEdited": True,
                "editedAt": message.get("edited", {}).get("ts", None),
                "editedBy": message.get("edited", {}).get("user", None),
                "text": message.get("text"),
                "isEmbed": False,
            }

            await database_service.update_message(message.get("ts"), message_data)
            logger.info(f"Message changed: {message.get("ts")}")

    elif event_type == "app_mention":
        user = event.get("user")
        response = client.conversations_open(users=user)

        return "Hi"  # TODO: Add logic to handle app mention

    elif event_type == "reaction_added":
        message_id = event.get("item").get("ts")
        reactions_data = [
            {
                "name": event.get("reaction"),
                "users": [event.get("user")],
                "messageId": message_id,
            }
        ]
        await database_service._create_reactions(message_id, reactions_data)
        logger.info(
            f"Reaction {event.get("reaction")} added to {message_id}: {event.get("user")}"
        )

    elif event_type == "reaction_removed":
        message_id = event.get("item").get("ts")
        reactions_data = [
            {
                "name": event.get("reaction"),
                "users": [event.get("user")],
                "messageId": message_id,
            }
        ]
        await database_service._delete_reactions(message_id, reactions_data)
        logger.info(
            f"Reaction {event.get("reaction")} removed from {message_id}: {event.get("user")}"
        )

    elif event_type == "team_join":
        user = event.get("user")
        await database_service.create_user(user)

    elif event_type == "user_change":
        user = event.get("user")
        await database_service.create_user(user)

    elif event_type == "member_joined_channel":
        user = event.get("user")
        await database_service.create_user(user)

    elif event_type == "member_left_channel":
        user = event.get("user")
        await database_service.create_user(user)

    elif event_type == "member_left_channel":
        user = event.get("user")
        await database_service.create_user(user)

    else:
        logger.debug(f"Unhandled event: {event_type}")
