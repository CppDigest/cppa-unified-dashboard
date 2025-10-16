import time
import json
import asyncio
import threading

from src.bot import SlackBot, eventApp, handler, RAGClient
from src.database import DatabaseService
from src.services import SlackDatabaseService, logger
from config.settings import Settings


async def start_socket_mode():
    """Start socket mode handler in background"""
    try:
        socket_handler = handler(eventApp, Settings.SLACK_APP_TOKEN)
        await socket_handler.start_async()
    except Exception as e:
        logger.error(f"Socket mode error: {e}")


async def main():
    """Main async function to handle database operations."""

    token = Settings.SLACK_BOT_TOKEN
    slack_bot = SlackBot(token=token)

    # Initialize database service
    db_service = DatabaseService()
    slack_db_service = SlackDatabaseService(slack_bot, db_service)
    rag_client = RAGClient()

    # Start RAG client
    loop_rag = asyncio.new_event_loop()
    threading.Thread(target=loop_rag.run_forever).start()
    asyncio.run_coroutine_threadsafe(rag_client.rag_sending_task(), loop_rag)
    # Start socket mode as a background task
    loop_socket = asyncio.new_event_loop()
    threading.Thread(target=loop_socket.run_forever).start()
    asyncio.run_coroutine_threadsafe(start_socket_mode(), loop_socket)

    try:

        logger.info("Available commands:")
        logger.info("  sync_all - Sync all data to database")
        logger.info("  rag_start - Start sending messages to RAG (100 per batch)")
        logger.info("  rag_stop - Stop sending messages to RAG")
        logger.info("  rag_progress - Check RAG sending progress")
        logger.info("  exit - Exit the program")

        while True:
            user_input = input(">> ").strip()
            try:

                if (
                    user_input.lower() == "exit"
                    or user_input.lower() == "q"
                    or user_input.lower() == "quit"
                ):
                    break

                elif user_input == "sync_all":
                    await slack_db_service.sync_all_users()
                    await slack_db_service.sync_all_data()

                elif user_input == "rag_start":
                    rag_client.start_sending()
                    logger.info(
                        "Started batch sending in background. Use 'rag_stop' to stop."
                    )
                elif user_input == "rag_stop":
                    rag_client.stop_sending()
                    logger.info("Stopped batch sending")
                elif user_input == "rag_progress":
                    progress = rag_client.get_progress()
                    logger.info(
                        f"Progress: RAG is {progress.get('status', 'stopped')} at {progress.get('last_sent_index', 0)} messages"
                    )
                else:
                    logger.warning("Invalid command")
            except Exception as e:
                logger.error(f"Error in main: {e}")

    except Exception as e:
        logger.error(f"Error in main: {e}")
    finally:
        if db_service:
            await db_service.disconnect()
        logger.info("Disconnected from database")


if __name__ == "__main__":
    asyncio.run(main())
