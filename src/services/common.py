from functools import wraps
import logging
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


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
