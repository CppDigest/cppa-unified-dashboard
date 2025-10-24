from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from slack_sdk import WebClient

from src.services import handle_event
from config.settings import Settings

event_app = AsyncApp(token=Settings.SLACK_BOT_TOKEN)
handler = AsyncSocketModeHandler
client = WebClient(token=Settings.SLACK_BOT_TOKEN)


@event_app.event("app_mention")
async def handle_app_mention_events(event, say):
    content = await handle_event(event, client)
    await say(content)


@event_app.event("message")
@event_app.event("reaction_added")
@event_app.event("reaction_removed")
@event_app.event("team_join")
@event_app.event("member_joined_channel")
@event_app.event("member_left_channel")
@event_app.event("user_change")
async def handle_events(event, say):
    await handle_event(event, client)


@event_app.command("/hi")
async def handle_some_command(ack, body, say):
    response = client.conversations_open(users=["U1234567890"])
    dm_channel = response["channel"]["id"]

    # Step 2: Send message in DM
    client.chat_postMessage(
        channel=dm_channel,
        text="Hey 👋 this is a private DM with the bot!",  # TODO: Add logic to handle command
    )
