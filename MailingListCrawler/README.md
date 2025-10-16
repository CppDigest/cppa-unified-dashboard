# Email Sync - Boost Mailing List Synchronization Tool

## Overview

`email_sync.py` is a Python script that incrementally synchronizes emails from Boost mailing lists to a target API. It fetches new emails, transforms them to the required format, and posts them in bundles with robust error handling and retry mechanisms.

## Features

- **Incremental Synchronization**: Tracks the last processed email for each mailing list to avoid re-processing
- **Batch Processing**: Bundles multiple emails (default: 5) into single API requests for efficiency
- **Retry Logic**: Implements exponential backoff for API failures, especially for rate limiting (429 errors)
- **Cache System**: Saves failed bundles to local cache files for later retry
- **Comprehensive Logging**: Logs all operations to both file and console
- **Connection Pooling**: Uses HTTP session with connection pooling for better performance
- **Field Mapping**: Automatically transforms email fields from Boost API format to target API format

## Requirements

Install dependencies using:

```bash
pip install -r requirements.txt
```

Dependencies:
- `requests==2.32.5`
- `urllib3==2.5.0`
- `certifi==2025.8.3`
- `charset-normalizer==3.4.3`
- `idna==3.10`
- `ijson==3.4.0`

## Setup

1. **Create Virtual Environment** (recommended):
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   pip install -r requirements.txt
   ```

2. **Configure Files**:
   - **`config.json`**: Main configuration file (required)
   - `pull.json`: Tracks last processed email hash for each list
   - `mailinglists/boost_mailing_lists.json`: Contains mailing list metadata

3. **Create `config.json`**:
   ```json
   {
     "file_paths": {
       "pull_file": "pull.json",
       "lists_file": "mailinglists/boost_mailing_lists.json",
       "cache_folder": "cache",
       "log_file": "email_sync.log"
     },
     "api_settings": {
       "endpoint": "http://192.168.1.8:8000/maillist/messages/new",
       "bundle_threshold": 5
     },
     "timing": {
       "request_delay": 0.5,
       "batch_delay": 1.0,
       "request_timeout": 30.0
     },
     "retry": {
       "max_attempts": 5,
       "initial_delay": 2.0,
       "backoff_multiplier": 2.0
     }
   }
   ```
   **Note**: The script will exit with an error if `config.json` is missing or invalid.

4. **Initial `pull.json` Structure**:
   ```json
   {
     "Boost-announce": "",
     "Boost-users": "",
     "Boost": ""
   }
   ```
   Note: Keys must match `display_name` from `boost_mailing_lists.json` (case-sensitive)

## Configuration

All configuration is managed through `config.json`. Edit this file to customize:

### File Paths
```json
"file_paths": {
  "pull_file": "pull.json",                    // Tracking file
  "lists_file": "mailinglists/boost_mailing_lists.json",  // Lists metadata
  "cache_folder": "cache",                     // Failed bundles cache
  "log_file": "email_sync.log"                // Log file
}
```

### API Settings
```json
"api_settings": {
  "endpoint": "http://192.168.1.8:8000/maillist/messages/new",
  "bundle_threshold": 5                        // Messages per bundle
}
```

### Timing Settings (seconds)
```json
"timing": {
  "request_delay": 0.5,                       // Delay between requests
  "batch_delay": 1.0,                         // Delay between batches
  "request_timeout": 30.0                     // Request timeout
}
```

### Retry Settings
```json
"retry": {
  "max_attempts": 5,                          // Max retry attempts
  "initial_delay": 2.0,                       // Initial retry delay
  "backoff_multiplier": 2.0                   // Backoff multiplier
}
```

**Important**: All sections and fields in `config.json` are required. The script will exit with a clear error message if any configuration is missing.

## Usage

### Run Once

```bash
python email_sync.py
```

### Run Continuously (Every 10 Minutes)

Use the provided batch file:

```bash
.\run_email_sync.bat
```

This will run the script in a loop, executing every 10 minutes. Press `Ctrl+C` to stop.

### Production Scheduling

For production environments, consider using Windows Task Scheduler or cron jobs:

**Windows Task Scheduler:**
```powershell
schtasks /create /tn "EmailSync" /tr "C:\path\to\venv\Scripts\python.exe C:\path\to\email_sync.py" /sc minute /mo 10
```

**Linux Cron:**
```bash
*/10 * * * * /path/to/venv/bin/python /path/to/email_sync.py
```

## How It Works

### Process Flow

1. **Load Configuration**: Reads `config.json` (required), `pull.json`, and `boost_mailing_lists.json`
2. **Validate Configuration**: Exits if `config.json` is missing or has invalid structure
3. **Process Cache Files**: Attempts to re-post any previously failed bundles
4. **Fetch New Emails**: For each mailing list:
   - Fetches emails from newest to oldest
   - Stops when reaching the last processed email hash
   - Collects full email content with retry on failures
   - Tracks metadata and content fetch failures separately
5. **Transform Data**: Maps fields from Boost API format to target API format:
   - `thread` → `thread_url`
   - `sender.address` → `sender_address`
   - `sender_name` → `from_field`
   - `mailinglist` URL → `to` (extracts email address)
6. **Bundle & Post**: Groups emails into bundles and posts to API
7. **Update Tracking**: Updates `pull.json` with the latest processed email hash
8. **Error Handling**: Saves failed bundles to cache for retry

### Field Mapping

The script transforms email fields to match the target API requirements:

| Source Field | Target Field | Example |
|-------------|--------------|---------|
| `thread` | `thread_url` | Direct mapping |
| `sender.address` | `sender_address` | Extracts from nested object |
| `sender_name` | `from_field` | Rename |
| `mailinglist` | `to` | Extracts email from URL |

### Request ID Generation

Each bundle gets a unique `requestId` generated by:
1. Collecting all `message_id_hash` values from the bundle
2. Sorting them for consistency
3. Creating a SHA256 hash of the concatenated values

This ensures idempotency - the same bundle always generates the same request ID.

## Error Handling

### Error Types

The script tracks and handles three distinct error types:

1. **`cache_failed`**: Cache file processing failed
   - Will retry on next run
   - Continues to next mailing list

2. **`collection_failed`**: Email metadata or content fetching failed
   - Stops after 3 consecutive metadata failures
   - Stops after 5 consecutive content failures
   - Logs detailed failure counts
   - Retries on next run

3. **`api_failed`**: API posting failed after all retries
   - Failed bundles saved to cache
   - Will retry cache files on next run

### Cache System

When an API call fails after all retry attempts:
- The bundle is saved to `cache/` folder
- Filename format: `{list_name}_cache_{timestamp}.json`
- On next run, cache files are processed before fetching new emails
- Successfully posted cache files are automatically deleted

### Rate Limiting (429 Errors)

**Unified handling for both GET and POST requests:**
- Respects `Retry-After` header from API responses
- Implements exponential backoff: 1s, 2s, 4s (for GET), 2s, 4s, 8s, 16s, 32s (for POST)
- Maximum 3 retry attempts for GET requests
- Maximum 5 retry attempts for POST requests (configurable in `config.json`)
- Logs retry attempts with request type (GET/POST)

### Timeout Errors

**Unified handling for both GET and POST requests:**
- Automatic retry with exponential backoff
- Logs retry attempts with request type (GET/POST)
- Maximum retries as configured in `config.json`

### Other Errors

- **5xx Server errors**: Handled by session-level retry (3 attempts, backoff 0.5)
- **4xx Client errors**: No retry (except 429)
- **JSON parsing errors**: Logged and skipped (non-transient)
- **Network errors**: Logged after session retry exhausted
- **File I/O errors**: Logged with detailed error messages

## Logging

All operations are logged to:
- **File**: `email_sync.log` (persisted)
- **Console**: Real-time output

Log format:
```
2025-10-12 14:30:45 - EmailSync - INFO - Starting Email Synchronization Process
```

Log levels:
- `INFO`: Normal operations
- `WARNING`: Recoverable issues (e.g., rate limiting)
- `ERROR`: Failures that require attention

## File Structure

```
project/
├── email_sync.py              # Main script
├── config.json                # Configuration file (required)
├── run_email_sync.bat         # Windows batch scheduler
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── pull.json                  # Last processed email tracking
├── email_sync.log             # Log file
├── mailinglists/
│   └── boost_mailing_lists.json
└── cache/                     # Failed bundles (created automatically)
    └── boost_cache_20251012_143045.json
```

## Troubleshooting

### Config file not found

**Cause**: `config.json` is missing

**Solution**: Create `config.json` with all required sections as shown in the Configuration section. The script will exit with a clear error message indicating what's missing.

### Invalid configuration

**Cause**: Missing required fields or sections in `config.json`

**Solution**: 
- Ensure all four sections exist: `file_paths`, `api_settings`, `timing`, `retry`
- Check that all fields within each section are present
- Verify JSON syntax is valid (no trailing commas, proper quotes)

### Script fetches all emails instead of only new ones

**Cause**: Key mismatch between `pull.json` and `boost_mailing_lists.json`

**Solution**: Ensure keys in `pull.json` exactly match the `display_name` field (case-sensitive):
```json
{
  "Boost-announce": "...",  // Not "boost-announce"
  "Boost-users": "...",     // Not "boost-users"
  "Boost": "..."            // Not "boost"
}
```

### API Validation Errors (422)

**Cause**: Missing required fields in the request

**Solution**: Ensure the `transform_message_format()` function correctly maps all required fields. Check API documentation for field requirements.

### Cache Files Not Being Processed

**Cause**: Cache file format mismatch or permission issues

**Solution**: 
- Check cache file structure matches expected format
- Verify write/read permissions on `cache/` folder
- Check logs for detailed error messages

### Rate Limiting Issues

**Cause**: Too many requests to the API

**Solution**:
- Increase `request_delay` and `batch_delay` in `config.json`
- Reduce `bundle_threshold` to send fewer messages per request
- Check API rate limits with your provider
- Review logs for 429 error patterns

### Collection Failures

**Cause**: Too many consecutive metadata or content fetch failures

**Solution**:
- Check network connectivity to source API
- Review `email_sync.log` for specific failure patterns
- Verify source API is accessible and responding
- Script will automatically retry on next run

## Best Practices

1. **Monitor Logs**: Regularly check `email_sync.log` for errors and warnings
2. **Backup Data**: Keep backups of `pull.json` and `config.json` before major changes
3. **Test Configuration**: Test with a small `bundle_threshold` first
4. **Cache Management**: Periodically review and clean old cache files
5. **API Limits**: Coordinate with API provider on rate limits
6. **Virtual Environment**: Always use a virtual environment for isolation
7. **Configuration Validation**: Test `config.json` changes by running the script once before scheduling

## Version History

- **v2.0**: 
  - Configuration moved to external `config.json` file
  - Unified error handling for GET and POST requests
  - Added detailed error type tracking (cache_failed, collection_failed, api_failed)
  - Improved retry logic with separate handling for 429 and timeout errors
  - Enhanced failure tracking for metadata and content fetching
  - Better code organization with modular functions
  
- **v1.0**: Initial release with incremental sync, caching, and retry logic

## Support

For issues or questions, check:
- Log file: `email_sync.log`
- Cache folder: `cache/`

## License

This tool is provided as-is for Boost mailing list synchronization purposes.

