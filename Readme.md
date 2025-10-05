# Slack Message Scraping Bot

A Slack bot for retrieving and managing Slack workspace messages.

## 📦 Installation

1. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your Slack tokens
   ```

## ⚙️ Configuration

### Environment Variables

```env
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token
```

### Required Slack App Permissions

- `channels:history` - Read message history

## 🚀 Usage

### Interactive CLI

```bash
python app.py
```

### Available Commands

- `fetch <channel_id>` - Get all messages from channel
- `exit` - Exit the bot
