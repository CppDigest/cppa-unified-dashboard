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


def handle_errors(default_return=None, log_prefix=""):
    """
    Decorator to handle common error patterns in Slack API calls.

    Args:
        default_return: Value to return on error
        log_prefix: Prefix for log messages
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"{log_prefix}Error in {func.__name__}: {e}")
                return default_return

        return wrapper

    return decorator


def get_message_url(channel_id: str, message_id: str) -> str:
    return f"https://my-office-team-hq.slack.com/archives/{channel_id}/p{message_id.replace('.', '')}"
