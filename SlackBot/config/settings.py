import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN", "")
    SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN", "")
    RAG_BASIC_URL = os.getenv("RAG_BASIC_URL", "")
    RAG_API_KEY = os.getenv("RAG_API_KEY", "")
