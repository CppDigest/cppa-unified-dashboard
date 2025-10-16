import uuid
import asyncio
from prisma.models import Message
import requests
import time
from typing import Dict, Any, Optional, List
from config.settings import Settings
from src.services import handle_errors, logger, get_message_url
from src.database import DatabaseService
from datetime import datetime


class RAGClient:
    """Client for sending data to the RAG (Retrieval-Augmented Generation) pipeline."""

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize the RAG client.

        Args:
            api_endpoint: API endpoint URL.
            api_key: API key for authentication.
        """
        self.db_service = None
        self.base_url = base_url or Settings.BASIC_URL_ENDPOINT
        self.api_key = api_key or Settings.RAG_API_KEY
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}" if self.api_key else "",
        }
        self.is_sending = False
        self.max_retries = 3
        self.default_retry_wait = 60
        self.batch_size = 100
        self.last_sent_index = 0

    def set_api_endpoint(self, api_endpoint: str) -> None:
        """
        Update the API endpoint.

        Args:
            api_endpoint: New API endpoint URL.
        """
        self.base_url = api_endpoint
        logger.info(f"RAG API endpoint updated to: {api_endpoint}")

    def set_api_key(self, api_key: str) -> None:
        """
        Update the API key.

        Args:
            api_key: New API key for authentication.
        """
        self.api_key = api_key
        self.headers["Authorization"] = f"Bearer {api_key}"
        logger.info("RAG API key updated")

    def set_batch_size(self, batch_size: int) -> None:
        """
        Update the batch size.

        Args:
            batch_size: New batch size.
        """
        self.batch_size = batch_size
        logger.info(f"Batch size updated to: {batch_size}")

    def _send_with_retry(
        self, url: str, data: Dict[str, Any], retries: int = 0
    ) -> Optional[Dict[str, Any]]:
        """
        Send data with automatic retry on 429 rate limit errors.

        Args:
            url: API endpoint URL.
            data: Data to send.
            retries: Current retry count.

        Returns:
            Response data or None on error.
        """
        try:
            response = requests.post(url, json=data, headers=self.headers, timeout=30)

            if response.status_code == 429:
                if retries >= self.max_retries:
                    logger.error(f"Max retries reached for rate limit on {url}")
                    return None

                retry_after = int(
                    response.headers.get("Retry-After", self.default_retry_wait)
                )
                logger.warning(
                    f"Rate limit hit (429). Waiting {retry_after}s before retry {retries + 1}/{self.max_retries}"
                )
                time.sleep(retry_after)
                return self._send_with_retry(url, data, retries + 1)

            if response.status_code == 422:
                logger.error(f"Unprocessable Entity (422). Response: {response.text}")
                return None

            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            logger.error(f"Request to RAG pipeline timed out: {url}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending data to RAG pipeline: {e}")
            if hasattr(e, "response") and e.response is not None:
                logger.error(f"Response body: {e.response.text}")
            return None

    @handle_errors(default_return=None, log_prefix="RAG Send Data ")
    def send_data(
        self, data: Dict[str, Any], endpoint_path: str = ""
    ) -> Optional[Dict[str, Any]]:
        """
        Send data to the RAG pipeline with automatic retry on rate limits.

        Args:
            data: Dictionary containing the data to send to the RAG pipeline.
            endpoint_path: Optional path to append to the base API endpoint.

        Returns:
            Response data from the RAG API or None on error.
        """
        url = f"{self.base_url}/{endpoint_path}" if endpoint_path else self.base_url

        result = self._send_with_retry(url, data)
        if result:
            logger.info(f"Successfully sent data to RAG pipeline at {url}")
        return result

    def format_message(self, message: Message) -> Dict[str, Any]:
        return {
            "message_id": f"@@Slack@@{message.channelId}_{message.id}",
            "subject": message.text,
            "content": message.text,
            "thread_url": get_message_url(
                message.channelId, message.threadTs if message.threadTs else message.id
            ),
            "sender_address": message.user.email if message.user.email else "",
            "from_field": (
                f"{message.user.realName} <{message.user.email}>"
                if message.user.email
                else ""
            ),
            "children": [],
            "date": message.timestamp.isoformat() if message.timestamp else "",
            "to": "",
            "cc": "",
            "reply_to": "",
            "parent": "",
            "url": get_message_url(message.channelId, message.id),
        }

    async def rag_sending_task(self) -> None:
        """RAG sending task"""

        while True:
            if not self.is_sending:
                continue

            if not self.db_service:
                self.db_service = DatabaseService()
                await self.db_service.connect()

            messages = await self.db_service.get_messages_for_rag(
                self.last_sent_index, self.batch_size
            )
            total_messages = len(messages)

            if self.last_sent_index == 0 and total_messages == 0:
                logger.info("No messages to send")
                continue

            if total_messages == 0:
                self.last_sent_index = 0
                continue

            logger.info(
                f"Total messages: {total_messages}, Starting from: {self.last_sent_index}"
            )

            messages_data = []
            for message in messages:
                message_dict = self.format_message(message)
                messages_data.append(message_dict)

            rag_send_data = {
                "timestamp": datetime.now().isoformat(),
                "requestId": f"slack@{str(uuid.uuid4())}",
                "messages": messages_data,
                "message_count": len(messages_data),
            }
            try:
                response = self.send_data(rag_send_data, "maillist/messages/new")

                if response and response.get("success") and "data" in response:
                    data = response.get("data", {})
                    failed_messages = data.get("failed_messages", [])
                    for message in messages:
                        if (
                            f"@@Slack@@{message.channelId}_{message.id}"
                            in failed_messages
                        ):
                            continue
                        await self.db_service.update_message(
                            message.id, {"isEmbed": True}
                        )

                    logger.info(
                        f"Progress: {total_messages - len(failed_messages)} success / {total_messages} total messages sent"
                    )

                    self.last_sent_index += len(messages) - len(failed_messages)
                    await asyncio.sleep(2)
                else:
                    logger.error(f"Failed to send batch. Stopping.{response}")
            except Exception as e:
                logger.error(f"Error sending batch: {e}")
                continue

    def start_sending(self):
        """Start the batch sending process."""
        self.is_sending = True

    def stop_sending(self):
        """Stop the batch sending process."""
        self.is_sending = False

    def get_progress(self) -> Dict[str, Any]:
        """Get current sending progress."""
        return {
            "status": "working" if self.is_sending else "stopped",
            "last_sent_index": self.last_sent_index,
            "timestamp": datetime.now().isoformat(),
        }
