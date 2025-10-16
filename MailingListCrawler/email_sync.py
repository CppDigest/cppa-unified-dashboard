"""
Email Synchronization Tool for Boost Mailing Lists

This script incrementally synchronizes emails from Boost mailing lists to a
target API with robust error handling, caching, and retry mechanisms.
"""

import os
import json
import time
import logging
import hashlib
import requests
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# ==================== Configuration ====================
class Config:
    """Configuration loaded from config.json"""
    
    # Default configuration file path
    CONFIG_FILE = "config.json"
    
    @classmethod
    def load_from_file(cls, config_file: str = None) -> None:
        """
        Load configuration from JSON file.
        Raises SystemExit if config file is not found or invalid.
        """
        if config_file is None:
            config_file = cls.CONFIG_FILE
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Load file paths (required section)
            file_paths = config_data.get('file_paths', {})
            if not file_paths:
                raise ValueError("Missing 'file_paths' section in config")
            
            cls.PULL_FILE = file_paths.get('pull_file')
            cls.LISTS_FILE = file_paths.get('lists_file')
            cls.CACHE_FOLDER = file_paths.get('cache_folder')
            cls.LOG_FILE = file_paths.get('log_file')
            
            # Validate required file paths
            if not all([cls.PULL_FILE, cls.LISTS_FILE, 
                       cls.CACHE_FOLDER, cls.LOG_FILE]):
                raise ValueError(
                    "Missing required fields in 'file_paths' section"
                )
            
            # Load API settings (required section)
            api_settings = config_data.get('api_settings', {})
            if not api_settings:
                raise ValueError("Missing 'api_settings' section in config")
            
            cls.API_ENDPOINT = api_settings.get('endpoint')
            cls.BUNDLE_THRESHOLD = api_settings.get('bundle_threshold')
            
            if not cls.API_ENDPOINT or cls.BUNDLE_THRESHOLD is None:
                raise ValueError(
                    "Missing required fields in 'api_settings' section"
                )
            
            # Load timing settings (required section)
            timing = config_data.get('timing', {})
            if not timing:
                raise ValueError("Missing 'timing' section in config")
            
            cls.REQUEST_DELAY = timing.get('request_delay')
            cls.BATCH_DELAY = timing.get('batch_delay')
            cls.REQUEST_TIMEOUT = timing.get('request_timeout')
            
            if any(x is None for x in [cls.REQUEST_DELAY, 
                                       cls.BATCH_DELAY, 
                                       cls.REQUEST_TIMEOUT]):
                raise ValueError(
                    "Missing required fields in 'timing' section"
                )
            
            # Load retry settings (required section)
            retry = config_data.get('retry', {})
            if not retry:
                raise ValueError("Missing 'retry' section in config")
            
            cls.MAX_RETRY_ATTEMPTS = retry.get('max_attempts')
            cls.INITIAL_RETRY_DELAY = retry.get('initial_delay')
            cls.RETRY_BACKOFF_MULTIPLIER = retry.get('backoff_multiplier')
            
            if any(x is None for x in [cls.MAX_RETRY_ATTEMPTS,
                                       cls.INITIAL_RETRY_DELAY,
                                       cls.RETRY_BACKOFF_MULTIPLIER]):
                raise ValueError(
                    "Missing required fields in 'retry' section"
                )
            
            print(f"Configuration loaded successfully from: {config_file}")
            
        except FileNotFoundError:
            print(f"ERROR: Configuration file '{config_file}' not found!")
            print("Please create config.json file before running.")
            raise SystemExit(1)
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON in '{config_file}': {e}")
            print("Please fix the JSON syntax in config.json.")
            raise SystemExit(1)
        except ValueError as e:
            print(f"ERROR: Invalid configuration: {e}")
            print("Please check config.json structure and required fields.")
            raise SystemExit(1)
        except Exception as e:
            print(f"ERROR: Failed to load configuration: {e}")
            raise SystemExit(1)


# ==================== Logging Setup ====================
def setup_logging() -> logging.Logger:
    """Configure and return logger with file and console handlers"""
    log_dir = os.path.dirname(Config.LOG_FILE)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    
    logger = logging.getLogger("EmailSync")
    logger.setLevel(logging.INFO)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # File handler
    file_handler = logging.FileHandler(
        Config.LOG_FILE, 
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


# ==================== File Operations ====================
def read_json_file(
    file_path: str, 
    logger: logging.Logger
) -> Optional[Dict[str, Any]]:
    """Read and parse JSON file with error handling"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"Successfully read: {file_path}")
        return data
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in {file_path}: {e}")
    except Exception as e:
        logger.error(f"Error reading {file_path}: {e}")
    return None


def write_json_file(
    file_path: str, 
    data: Dict[str, Any], 
    logger: logging.Logger
) -> bool:
    """Write data to JSON file with error handling"""
    try:
        file_dir = os.path.dirname(file_path)
        if file_dir:
            os.makedirs(file_dir, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Successfully wrote: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error writing {file_path}: {e}")
        return False


def normalize_list_name(list_name: str) -> str:
    """Normalize mailing list name for use in filenames"""
    normalized = list_name.lower()
    normalized = normalized.replace(' ', '_').replace('-', '_')
    normalized = ''.join(
        c if c.isalnum() or c == '_' else '' 
        for c in normalized
    )
    return normalized


# ==================== Cache Management ====================
def save_cache_file(
    list_name: str, 
    bundle_data: List[Dict[str, Any]], 
    logger: logging.Logger
) -> str:
    """Save failed bundle to timestamped cache file"""
    os.makedirs(Config.CACHE_FOLDER, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    normalized_name = normalize_list_name(list_name)
    cache_filename = f"{normalized_name}_cache_{timestamp}.json"
    cache_path = os.path.join(Config.CACHE_FOLDER, cache_filename)
    
    cache_data = {
        "timestamp": datetime.now().isoformat(),
        "list_name": list_name,
        "message_count": len(bundle_data),
        "messages": bundle_data
    }
    
    if write_json_file(cache_path, cache_data, logger):
        logger.info(f"Saved cache: {cache_path}")
        return cache_path
    return ""


def get_cache_files(
    list_name: str, 
    logger: logging.Logger
) -> List[str]:
    """Get all cache files for a specific mailing list"""
    if not os.path.exists(Config.CACHE_FOLDER):
        return []
    
    cache_files = []
    normalized_name = normalize_list_name(list_name)
    pattern = f"{normalized_name}_cache_"
    
    try:
        for filename in os.listdir(Config.CACHE_FOLDER):
            if filename.startswith(pattern) and filename.endswith('.json'):
                cache_path = os.path.join(Config.CACHE_FOLDER, filename)
                cache_files.append(cache_path)
        
        cache_files.sort()  # Sort by timestamp
        
        if cache_files:
            logger.info(
                f"Found {len(cache_files)} cache file(s) for {list_name}"
            )
        
        return cache_files
    except Exception as e:
        logger.error(f"Error reading cache folder: {e}")
        return []


def process_single_cache_file(
    cache_path: str,
    api_endpoint: str,
    session: requests.Session,
    logger: logging.Logger
) -> bool:
    """Process a single cache file and delete if successful"""
    logger.info(f"Processing cache: {cache_path}")
    
    cache_data = read_json_file(cache_path, logger)
    if not cache_data:
        logger.error(f"Failed to read cache: {cache_path}")
        return True  # Continue to next file
    
    messages = cache_data.get('messages', [])
    if not messages:
        logger.warning(f"Empty cache: {cache_path}")
        try:
            os.remove(cache_path)
            logger.info(f"Removed empty cache: {cache_path}")
        except Exception as e:
            logger.error(f"Failed to remove cache: {e}")
        return True
    
    logger.info(f"Posting {len(messages)} messages from cache")
    success = post_bundle_with_retry(
        api_endpoint, 
        messages, 
        session, 
        logger
    )
    
    if success:
        try:
            os.remove(cache_path)
            logger.info(f"Posted and removed cache: {cache_path}")
        except Exception as e:
            logger.error(f"Failed to remove cache: {e}")
        return True
    else:
        logger.error(f"Failed to post cache: {cache_path}")
        return False


def process_all_cache_files(
    list_name: str,
    api_endpoint: str,
    session: requests.Session,
    logger: logging.Logger
) -> bool:
    """Process all cache files for a mailing list"""
    cache_files = get_cache_files(list_name, logger)
    
    if not cache_files:
        logger.info(f"No cache files for {list_name}")
        return True
    
    logger.info(f"Processing {len(cache_files)} cache file(s)")
    
    for cache_path in cache_files:
        success = process_single_cache_file(
            cache_path, 
            api_endpoint, 
            session, 
            logger
        )
        if not success:
            logger.error(f"Cache processing failed, stopping")
            return False
    
    logger.info(f"Completed cache processing for {list_name}")
    return True


# ==================== HTTP Session ====================
def create_http_session() -> requests.Session:
    """Create HTTP session with connection pooling and retry strategy"""
    session = requests.Session()
    
    # Retry strategy (excluding 429 - handled separately)
    retry_strategy = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
    )
    
    adapter = HTTPAdapter(
        max_retries=retry_strategy,
        pool_connections=10,
        pool_maxsize=20
    )
    
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session


# ==================== API Requests ====================
def extract_retry_after(
    response: requests.Response,
    default_delay: float
) -> int:
    """Extract retry_after value from response headers"""
    return int(response.headers.get('Retry-After', default_delay))


def handle_rate_limit_response(
    response: requests.Response,
    attempt: int,
    max_retries: int,
    retry_delay: float,
    url: str,
    logger: logging.Logger,
    is_post: bool = False
) -> Tuple[bool, float]:
    """
    Handle 429 rate limit response for both GET and POST requests.
    Returns (should_continue, new_retry_delay)
    """
    retry_after = extract_retry_after(response, retry_delay)
    
    if attempt < max_retries - 1:
        request_type = "POST" if is_post else "GET"
        logger.warning(
            f"Rate limited (429) on {request_type}. "
            f"Retry {attempt + 1}/{max_retries} "
            f"after {retry_after}s: {url}"
        )
        time.sleep(retry_after)
        return True, retry_delay * 2
    else:
        logger.error(
            f"Rate limit exceeded, no retries left: {url}"
        )
        return False, retry_delay


def handle_timeout_error(
    attempt: int,
    max_retries: int,
    retry_delay: float,
    url: str,
    logger: logging.Logger,
    is_post: bool = False
) -> Tuple[bool, float]:
    """
    Handle timeout exception for both GET and POST requests.
    Returns (should_continue, new_retry_delay)
    """
    if attempt < max_retries - 1:
        request_type = "POST" if is_post else "GET"
        logger.warning(
            f"Timeout on {request_type}. "
            f"Retry {attempt + 1}/{max_retries} "
            f"after {retry_delay}s: {url}"
        )
        time.sleep(retry_delay)
        return True, retry_delay * 2
    else:
        logger.error(f"Timeout, no retries left: {url}")
        return False, retry_delay


def fetch_json_from_url(
    url: str,
    session: requests.Session,
    logger: logging.Logger,
    max_retries: int = 3
) -> Optional[Dict[str, Any]]:
    """
    Fetch JSON data from URL with retry logic and exponential backoff.
    Handles 429 rate limiting and timeouts with retry.
    5xx errors are handled by session-level retry strategy.
    """
    retry_delay = 1.0  # Start with 1 second delay
    
    for attempt in range(max_retries):
        try:
            response = session.get(url, timeout=Config.REQUEST_TIMEOUT)
            
            # Handle rate limiting (429) - not in session retry
            if response.status_code == 429:
                should_continue, retry_delay = handle_rate_limit_response(
                    response, attempt, max_retries, 
                    retry_delay, url, logger, is_post=False
                )
                if should_continue:
                    continue
                else:
                    return None
            
            # Raise for other HTTP errors (4xx, 5xx)
            # Note: 5xx will be retried by session-level retry first
            response.raise_for_status()
            
            # Parse and return JSON
            return response.json()
            
        except requests.exceptions.Timeout:
            should_continue, retry_delay = handle_timeout_error(
                attempt, max_retries, retry_delay, url, logger
            )
            if not should_continue:
                return None
                
        except requests.exceptions.RequestException as e:
            # Other request errors (after session retry exhausted)
            logger.error(f"Request error for {url}: {e}")
            return None
                
        except json.JSONDecodeError as e:
            # JSON decode errors are not transient, don't retry
            logger.error(f"JSON decode error for {url}: {e}")
            return None
    
    return None


def fetch_email_metadata(
    url: str,
    session: requests.Session,
    logger: logging.Logger
) -> Optional[Dict[str, Any]]:
    """Fetch email metadata from API"""
    return fetch_json_from_url(url, session, logger)


def fetch_email_content(
    url: str,
    session: requests.Session,
    logger: logging.Logger
) -> Optional[Dict[str, Any]]:
    """Fetch full email content from API"""
    logger.info(f"Fetching content: {url}")
    return fetch_json_from_url(url, session, logger)


# ==================== Message Transformation ====================
def extract_to_address(mailinglist_url: str) -> str:
    """Extract email address from mailinglist URL"""
    if '/list/' in mailinglist_url:
        # Extract: "http://.../list/boost@lists.boost.org/" 
        # -> "boost@lists.boost.org"
        to_address = mailinglist_url.split('/list/')[-1].rstrip('/')
        return to_address
    return ""


def transform_message_format(
    message: Dict[str, Any]
) -> Dict[str, Any]:
    """Transform message from Boost API format to target API format"""
    transformed = message.copy()
    
    # Map 'thread' to 'thread_url'
    if 'thread' in transformed:
        transformed['thread_url'] = transformed.pop('thread')
    
    # Map 'sender.address' to 'sender_address'
    sender = transformed.get('sender', {})
    if isinstance(sender, dict) and 'address' in sender:
        transformed['sender_address'] = sender['address']
    
    # Map 'sender_name' to 'from_field'
    if 'sender_name' in transformed:
        transformed['from_field'] = transformed.pop('sender_name')
    
    # Extract 'to' from 'mailinglist' URL
    mailinglist_url = transformed.get('mailinglist', '')
    transformed['to'] = extract_to_address(mailinglist_url)
    
    return transformed


def generate_request_id(messages: List[Dict[str, Any]]) -> str:
    """Generate SHA256 hash request ID from message hashes"""
    message_hashes = [
        msg.get('message_id_hash', '')
        for msg in messages
        if msg.get('message_id_hash')
    ]
    
    combined = ''.join(sorted(message_hashes))
    hash_object = hashlib.sha256(combined.encode('utf-8'))
    return hash_object.hexdigest()


# ==================== API Posting ====================
def build_request_data(
    messages: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Build request data structure for API POST"""
    transformed_messages = [
        transform_message_format(msg) 
        for msg in messages
    ]
    
    request_data = {
        "timestamp": datetime.now().isoformat(),
        "requestId": generate_request_id(messages),
        "messages": transformed_messages,
        "message_count": len(transformed_messages)
    }
    
    return request_data


def post_messages_bundle(
    api_endpoint: str,
    request_data: Dict[str, Any],
    session: requests.Session,
    logger: logging.Logger,
    attempt: int = 0,
    max_retries: int = None,
    retry_delay: float = None
) -> Tuple[bool, float]:
    """
    POST messages bundle to API endpoint with 429 and timeout handling.
    Returns (success, new_retry_delay)
    """
    if max_retries is None:
        max_retries = Config.MAX_RETRY_ATTEMPTS
    if retry_delay is None:
        retry_delay = Config.INITIAL_RETRY_DELAY
    
    try:
        message_count = request_data.get('message_count', 0)
        logger.info(f"Posting {message_count} messages to API")
        logger.info(f"Request ID: {request_data['requestId']}")
        
        response = session.post(
            api_endpoint,
            json=request_data,
            timeout=Config.REQUEST_TIMEOUT,
            headers={"Content-Type": "application/json"}
        )
        
        # Handle rate limiting (429) using common handler
        if response.status_code == 429:
            should_continue, new_retry_delay = handle_rate_limit_response(
                response, attempt, max_retries,
                retry_delay, api_endpoint, logger, is_post=True
            )
            # Return success=False and updated delay
            return False, new_retry_delay
        
        # Handle success
        if 200 <= response.status_code < 300:
            logger.info(f"Success: {response.status_code}")
            return True, retry_delay
        
        # Handle other errors
        logger.error(
            f"POST failed ({response.status_code}): {response.text}"
        )
        return False, retry_delay
    
    except requests.exceptions.Timeout:
        # Handle timeout using common handler
        should_continue, new_retry_delay = handle_timeout_error(
            attempt, max_retries, retry_delay, 
            api_endpoint, logger, is_post=True
        )
        return False, new_retry_delay
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error posting bundle: {e}")
        return False, retry_delay


def post_bundle_with_retry(
    api_endpoint: str,
    messages: List[Dict[str, Any]],
    session: requests.Session,
    logger: logging.Logger
) -> bool:
    """POST bundle with exponential backoff retry logic"""
    retry_delay = Config.INITIAL_RETRY_DELAY
    
    # Build request data once before retry loop
    request_data = build_request_data(messages)
    
    for attempt in range(Config.MAX_RETRY_ATTEMPTS):
        success, retry_delay = post_messages_bundle(
            api_endpoint, 
            request_data,  # Pass pre-built request data
            session, 
            logger,
            attempt,
            Config.MAX_RETRY_ATTEMPTS,
            retry_delay
        )
        
        if success:
            return True
        
        # Wait before next retry if not last attempt
        if attempt < Config.MAX_RETRY_ATTEMPTS - 1:
            # Sleep already done in handle_rate_limit_response for 429
            # For other errors, we need to wait
            pass  # Delay is handled by handle_rate_limit_response for 429
    
    logger.error(
        f"Failed after {Config.MAX_RETRY_ATTEMPTS} attempts"
    )
    return False


# ==================== Email Collection ====================
def fetch_single_email(
    emails_url: str,
    offset: int,
    session: requests.Session,
    logger: logging.Logger
) -> Optional[Dict[str, Any]]:
    """Fetch a single email at the given offset"""
    iterate_url = f"{emails_url}?limit=1&offset={offset}"
    logger.info(f"Fetching email at offset {offset}")
    
    iterate_email = fetch_email_metadata(iterate_url, session, logger)
    
    if not iterate_email:
        logger.error(f"Failed to fetch at offset {offset}")
        return None
    
    results = iterate_email.get('results', [])
    if not results:
        logger.info(f"No more emails at offset {offset}")
        return None
    
    return results[0]


class EmailCollectionResult:
    """Result of email collection process"""
    def __init__(
        self,
        emails: List[Dict[str, Any]],
        success: bool = True,
        failed_metadata_count: int = 0,
        failed_content_count: int = 0
    ):
        self.emails = emails
        self.success = success
        self.failed_metadata_count = failed_metadata_count
        self.failed_content_count = failed_content_count


def collect_new_emails(
    emails_url: str,
    last_processed_hash: str,
    session: requests.Session,
    logger: logging.Logger
) -> EmailCollectionResult:
    """
    Collect all new emails until reaching last processed.
    Returns EmailCollectionResult with collected emails and failure counts.
    """
    new_emails = []
    offset = 0
    failed_metadata_count = 0
    failed_content_count = 0
    consecutive_metadata_failures = 0
    consecutive_content_failures = 0
    
    while True:
        result = fetch_single_email(emails_url, offset, session, logger)
        
        if not result:
            failed_metadata_count += 1
            consecutive_metadata_failures += 1
            
            # Stop if too many consecutive metadata failures
            if consecutive_metadata_failures >= 3:
                logger.error(
                    f"Too many consecutive metadata fetch failures "
                    f"(offset {offset}). Stopping collection."
                )
                return EmailCollectionResult(
                    emails=new_emails,
                    success=False,
                    failed_metadata_count=failed_metadata_count,
                    failed_content_count=failed_content_count
                )
            
            # If no results at all, we've reached the end
            if offset == 0:
                break
            
            offset += 1
            time.sleep(Config.REQUEST_DELAY)
            continue
        
        # Reset consecutive metadata failure counter on success
        consecutive_metadata_failures = 0
        
        message_id_hash = result.get('message_id_hash', '')
        email_url = result.get('url', '')
        
        logger.info(f"Found email: {message_id_hash}")
        
        # Check if reached last processed
        if message_id_hash == last_processed_hash:
            logger.info(f"Reached last processed: {message_id_hash}")
            break
        
        # Fetch full content
        if email_url:
            time.sleep(Config.REQUEST_DELAY)
            email_content = fetch_email_content(email_url, session, logger)
            
            if email_content:
                new_emails.append(email_content)
                consecutive_content_failures = 0  # Reset on success
                logger.info(
                    f"Fetched content (total: {len(new_emails)})"
                )
            else:
                failed_content_count += 1
                consecutive_content_failures += 1
                logger.error(f"Failed to fetch content: {email_url}")
                
                # Stop if too many consecutive content failures
                if consecutive_content_failures >= 5:
                    logger.error(
                        f"Too many consecutive content fetch failures "
                        f"({consecutive_content_failures}). "
                        f"Stopping collection."
                    )
                    return EmailCollectionResult(
                        emails=new_emails,
                        success=False,
                        failed_metadata_count=failed_metadata_count,
                        failed_content_count=failed_content_count
                    )
        
        offset += 1
        time.sleep(Config.REQUEST_DELAY)
    
    # Log summary if there were failures
    if failed_metadata_count > 0 or failed_content_count > 0:
        logger.warning(
            f"Collection completed with failures: "
            f"{failed_metadata_count} metadata, "
            f"{failed_content_count} content"
        )
    
    return EmailCollectionResult(
        emails=new_emails,
        success=True,
        failed_metadata_count=failed_metadata_count,
        failed_content_count=failed_content_count
    )


# ==================== Bundle Processing ====================
def process_email_bundles(
    new_emails: List[Dict[str, Any]],
    list_name: str,
    api_endpoint: str,
    session: requests.Session,
    logger: logging.Logger
) -> bool:
    """Process collected emails in bundles"""
    if not new_emails:
        logger.info(f"No new emails for {list_name}")
        return True
    
    logger.info(f"Processing {len(new_emails)} emails in bundles")
    
    # Reverse to process oldest first
    new_emails.reverse()
    
    # Calculate total bundles
    total_bundles = (
        (len(new_emails) + Config.BUNDLE_THRESHOLD - 1) 
        // Config.BUNDLE_THRESHOLD
    )
    
    # Process each bundle
    for idx in range(0, len(new_emails), Config.BUNDLE_THRESHOLD):
        bundle_end = min(idx + Config.BUNDLE_THRESHOLD, len(new_emails))
        bundle = new_emails[idx:bundle_end]
        bundle_num = (idx // Config.BUNDLE_THRESHOLD) + 1
        
        logger.info(
            f"Bundle {bundle_num}/{total_bundles} "
            f"({len(bundle)} messages)"
        )
        
        success = post_bundle_with_retry(
            api_endpoint, 
            bundle, 
            session, 
            logger
        )
        
        if not success:
            logger.error(f"Failed bundle {bundle_num}/{total_bundles}")
            cache_path = save_cache_file(list_name, bundle, logger)
            logger.error(f"Saved to cache: {cache_path}")
            logger.error(f"Terminated for {list_name}")
            return False
        
        # Delay between bundles
        if bundle_end < len(new_emails):
            time.sleep(Config.BATCH_DELAY)
    
    logger.info(f"Successfully processed {len(new_emails)} emails")
    return True


def update_pull_file(
    pull_data: Dict[str, str],
    list_name: str,
    latest_hash: str,
    logger: logging.Logger
) -> None:
    """Update pull.json with latest processed hash"""
    pull_data[list_name] = latest_hash
    write_json_file(Config.PULL_FILE, pull_data, logger)
    logger.info(f"Updated pull.json with hash: {latest_hash}")


# ==================== List Processing ====================
class ProcessingResult:
    """Result of processing a single mailing list"""
    def __init__(
        self, 
        success: bool, 
        error_type: Optional[str] = None,
        error_message: Optional[str] = None
    ):
        self.success = success
        self.error_type = error_type  # 'cache_failed', 'api_failed', etc.
        self.error_message = error_message


def process_single_list(
    list_info: Dict[str, Any],
    pull_data: Dict[str, str],
    api_endpoint: str,
    session: requests.Session,
    logger: logging.Logger
) -> ProcessingResult:
    """
    Process emails for a single mailing list.
    Returns ProcessingResult with success status and error details.
    """
    display_name = list_info['display_name']
    emails_url = list_info['emails']
    last_processed_hash = pull_data.get(display_name, "")
    
    logger.info("=" * 50)
    logger.info(f"Processing list: {display_name}")
    logger.info(f"Last processed: {last_processed_hash}")
    
    # Step 1: Process cache files
    logger.info(f"Step 1: Processing cache for {display_name}")
    cache_success = process_all_cache_files(
        display_name, 
        api_endpoint, 
        session, 
        logger
    )
    if not cache_success:
        error_msg = f"Failed to process cache files for {display_name}"
        logger.error(error_msg)
        return ProcessingResult(
            success=False,
            error_type="cache_failed",
            error_message=error_msg
        )
    
    # Step 2: Collect new emails
    logger.info(f"Step 2: Collecting new emails")
    collection_result = collect_new_emails(
        emails_url,
        last_processed_hash,
        session,
        logger
    )
    
    # Check if collection failed critically
    if not collection_result.success:
        error_msg = (
            f"Failed to collect emails for {display_name}. "
            f"Metadata failures: {collection_result.failed_metadata_count}, "
            f"Content failures: {collection_result.failed_content_count}"
        )
        logger.error(error_msg)
        return ProcessingResult(
            success=False,
            error_type="collection_failed",
            error_message=error_msg
        )
    
    # Check if there were partial failures
    if collection_result.failed_content_count > 0:
        logger.warning(
            f"{collection_result.failed_content_count} emails failed "
            f"to fetch content for {display_name}"
        )
    
    new_emails = collection_result.emails
    
    # Step 3: Update pull.json with latest hash
    if new_emails:
        latest_hash = new_emails[0].get('message_id_hash', '')
        if latest_hash:
            update_pull_file(pull_data, display_name, latest_hash, logger)
    
    # Step 4: Process emails in bundles
    logger.info(f"Step 3: Processing email bundles")
    success = process_email_bundles(
        new_emails,
        display_name,
        api_endpoint,
        session,
        logger
    )
    
    if not success:
        error_msg = (
            f"Failed to post email bundles for {display_name}. "
            f"Check cache folder for failed bundles."
        )
        logger.error(error_msg)
        return ProcessingResult(
            success=False,
            error_type="api_failed",
            error_message=error_msg
        )
    
    return ProcessingResult(success=True)


# ==================== Main Entry Point ====================
def main():
    """Main execution function"""
    # Load configuration from config.json
    print("Loading configuration from config.json...")
    Config.load_from_file()
    
    logger = setup_logging()
    logger.info("=" * 50)
    logger.info("Starting Email Synchronization Process")
    logger.info("=" * 50)
    logger.info(f"Configuration loaded from: {Config.CONFIG_FILE}")
    
    # Load configuration files
    pull_data = read_json_file(Config.PULL_FILE, logger)
    if pull_data is None:
        logger.error("Failed to read pull.json. Exiting.")
        return
    
    lists_data = read_json_file(Config.LISTS_FILE, logger)
    if lists_data is None:
        logger.error("Failed to read boost_mailing_lists.json. Exiting.")
        return
    
    mailing_lists = lists_data.get('lists', [])
    logger.info(f"Found {len(mailing_lists)} mailing lists")
    
    # Create HTTP session
    session = create_http_session()
    api_endpoint = Config.API_ENDPOINT
    logger.info(f"API endpoint: {api_endpoint}")
    
    # Process each mailing list
    for idx, list_info in enumerate(mailing_lists, 1):
        display_name = list_info.get('display_name', 'Unknown')
        logger.info(f"\nList {idx}/{len(mailing_lists)}: {display_name}")
        
        result = process_single_list(
            list_info,
            pull_data,
            api_endpoint,
            session,
            logger
        )
        
        if not result.success:
            # Handle different error types
            if result.error_type == "cache_failed":
                logger.error(
                    f"Cache processing failed for {display_name}. "
                    f"Will retry on next run."
                )
                # Continue to next list - cache will be retried later
                
            elif result.error_type == "collection_failed":
                logger.error(
                    f"Email collection failed for {display_name}. "
                    f"Details: {result.error_message}"
                )
                # Continue to next list - will retry collection on next run
                
            elif result.error_type == "api_failed":
                logger.error(
                    f"API posting failed for {display_name}. "
                    f"Failed bundles saved to cache folder."
                )
                # Continue to next list - failed bundles are cached
                
            else:
                logger.error(
                    f"Unknown error for {display_name}: "
                    f"{result.error_message}"
                )
        else:
            logger.info(f"Successfully completed {display_name}")
        
        # Delay between lists
        if idx < len(mailing_lists):
            time.sleep(Config.BATCH_DELAY)
    
    logger.info("=" * 50)
    logger.info("Email Synchronization Process Completed")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
