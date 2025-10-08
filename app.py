import threading
import json
import asyncio

from src.bot import SlackBot
from src.database import DatabaseService
from src.services import SlackDatabaseService, logger
from config.settings import Settings


async def main():
    """Main async function to handle database operations."""
    token = Settings.SLACK_BOT_TOKEN
    slackBot = SlackBot(token=token)

    # Initialize database service
    dbService = DatabaseService()
    slackDbService = SlackDatabaseService(slackBot, dbService)

    try:
        await dbService.connect()
        logger.info("Connected to PostgreSQL database")

        logger.info("Available commands:")
        logger.info("  fetch <channelId> - Fetch all messages from a channel")
        logger.info("  sync <channelId> - Sync all data to database")
        logger.info("  sync_users - Sync all users to database")
        logger.info("  get_db <channelId> - Get messages from database")
        logger.info("  search <query> - Search messages in database")
        logger.info("  user_db <userId> - Get user messages from database")
        logger.info("  thread_db <threadTs> - Get thread messages from database")
        logger.info("  thread <threadTs> - Get all messages in a thread")
        logger.info("  user <userId> - Get user information")
        logger.info("  users - Get all users in workspace")
        logger.info("  profile <userId> - Get user profile")
        logger.info("  lookup <email> - Look up user by email")
        logger.info("  exit - Exit the program")

        while True:
            userInput = input(">> ").strip()
            if (
                userInput.lower() == "exit"
                or userInput.lower() == "q"
                or userInput.lower() == "quit"
            ):
                break
            elif userInput.startswith("fetch"):
                _, channelId = userInput.split()
                slackBot.set_channel_id(channelId)
                res = slackBot.get_all_history()
                with open("ref/all_messages.json", "w", encoding="utf-8") as f:
                    json.dump(res, f)
                logger.info(f"Saved {len(res)} messages to all_messages.json")
            elif userInput.startswith("sync "):
                _, channelId = userInput.split()
                result = await slackDbService.sync_all_data(channelId)
                logger.info(
                    f"Synced {result['users']} users and {result['messages']} messages to database"
                )
            elif userInput == "sync_users":
                count = await slackDbService.sync_user_data()
                logger.info(f"Synced {count} users to database")
            elif userInput.startswith("get_db "):
                _, channelId = userInput.split()
                res = await slackDbService.get_channel_messages_from_db(channelId)
                with open("ref/db_messages.json", "w", encoding="utf-8") as f:
                    json.dump(res, f)
                logger.info(f"Retrieved {len(res)} messages from database")
            elif userInput.startswith("search "):
                _, query = userInput.split()
                res = await slackDbService.search_messages_in_db(query)
                with open("ref/search_results.json", "w", encoding="utf-8") as f:
                    json.dump(res, f)
                logger.info(f"Found {len(res)} messages matching '{query}'")
            elif userInput.startswith("user_db "):
                _, userId = userInput.split()
                res = await slackDbService.get_user_messages_from_db(userId)
                with open("ref/user_messages_db.json", "w", encoding="utf-8") as f:
                    json.dump(res, f)
                logger.info(f"Retrieved {len(res)} messages from user {userId}")
            elif userInput.startswith("thread_db "):
                _, threadTs = userInput.split()
                res = await slackDbService.get_thread_messages_from_db(threadTs)
                with open("ref/thread_messages_db.json", "w", encoding="utf-8") as f:
                    json.dump(res, f)
                logger.info(f"Retrieved {len(res)} thread messages from database")
            elif userInput.startswith("thread"):
                _, threadTs = userInput.split()
                res = slackBot.get_thread_by_root_message(threadTs)
                with open("ref/thread_messages.json", "w", encoding="utf-8") as f:
                    json.dump(res, f)
                logger.info(f"Saved {len(res)} messages to thread_messages.json")
                logger.info(f"Found {len(res)} messages in thread {threadTs}")
                for i, msg in enumerate(res):
                    logger.info(
                        f"  {i+1}. {msg.get('text', 'No text')} (by {msg.get('user', 'Unknown')})"
                    )
            elif userInput == "users":
                res = slackBot.get_all_users()
                with open("ref/all_users.json", "w", encoding="utf-8") as f:
                    json.dump(res, f)
                logger.info(f"Saved {len(res)} users to all_users.json")
            elif userInput.startswith("user"):
                _, userId = userInput.split()
                res = slackBot.get_user_info(userId)
                with open("ref/user_info.json", "w", encoding="utf-8") as f:
                    json.dump(res, f)
                logger.info(f"Saved user info to user_info.json")
                if res:
                    logger.info(
                        f"User: {res.get('real_name', 'Unknown')} ({res.get('name', 'Unknown')})"
                    )
                    logger.info(
                        f"Email: {res.get('profile', {}).get('email', 'Not available')}"
                    )
                    logger.info(
                        f"Status: {res.get('profile', {}).get('status_text', 'No status')}"
                    )
                    logger.info(f"Is Bot: {res.get('is_bot', False)}")
                    logger.info(f"Deleted: {res.get('deleted', False)}")
                else:
                    logger.warning("User not found")
            elif userInput.startswith("profile"):
                _, userId = userInput.split()
                res = slackBot.get_user_profile(userId)
                with open("ref/user_profile.json", "w", encoding="utf-8") as f:
                    json.dump(res, f)
                logger.info(f"Saved user profile to user_profile.json")
                if res:
                    logger.info(f"Profile: {res}")
                else:
                    logger.warning("Profile not found")
            elif userInput.startswith("lookup"):
                _, email = userInput.split()
                res = slackBot.lookup_user_by_email(email)
                with open("ref/user_lookup.json", "w", encoding="utf-8") as f:
                    json.dump(res, f)
                logger.info(f"Saved user lookup to user_lookup.json")
                if res:
                    logger.info(
                        f"Found user: {res.get('real_name', 'Unknown')} ({res.get('name', 'Unknown')})"
                    )
                else:
                    logger.warning("User not found")
            else:
                logger.warning("Invalid command")
    except Exception as e:
        logger.error(f"Error in main: {e}")
    finally:
        # if dbService:
        #     await dbService.disconnect()
        logger.info("Disconnected from database")


if __name__ == "__main__":
    asyncio.run(main())
