import logging

logger = logging.getLogger(__name__)


def handle_event(event: dict):
    eventType = event.get("type")
    if eventType == "message" and "subtype" not in event:
        user = event.get("user")
        text = event.get("text")
        channel = event.get("channel")
        ts = event.get("ts")
        logger.info(f"[{channel}] {user}: {text} ({ts})")
    elif eventType == "reaction_added":
        logger.info(f"Reaction added: {event}")
    else:
        logger.debug(f"Unhandled event: {eventType}")
