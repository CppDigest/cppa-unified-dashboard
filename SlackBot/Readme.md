# CPPA Unified Dashboard - Slack Bot

A comprehensive Slack bot with real-time event handling, message scraping, and PostgreSQL database integration for managing Slack workspace data.

## 📦 Installation

1. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Install PostgreSQL (local development)**

   - Windows: Download installer from `https://www.postgresql.org/download/windows/` and follow the setup (remember the password for the `postgres` user).
   - macOS: `brew install postgresql` then `brew services start postgresql`.
   - Linux (Debian/Ubuntu):

     ```bash
     sudo apt update && sudo apt install -y postgresql postgresql-contrib
     sudo systemctl enable --now postgresql
     ```

   Create a database for this app (replace values as needed):

   ```bash
   # psql shell
   psql -U postgres
   -- inside psql
   CREATE DATABASE slack_database;
   -- optionally create a dedicated user
   CREATE USER slack_user WITH ENCRYPTED PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE slack_database TO slack_user;
   ```

   The resulting connection URL will be:

   ```
   postgresql://slack_user:your_password@localhost:5432/slack_database
   ```

3. **Set up environment variables**

   ```bash
   cp env.example .env
   # Edit .env with your Slack tokens
   ```

4. **Initialize Prisma database**

   With your `DATABASE_URL` set in `.env`, push the Prisma schema and generate the client:

   ```bash
   # create a named migration in dev workflows
   prisma migrate dev --name init
   ```

## ⚙️ Configuration

### Slack App Setup

For detailed Slack App configuration including:

- **Bot OAuth Scopes** - All required permissions
- **Event Subscriptions** - Real-time event configuration
- **Socket Mode Setup** - Step-by-step implementation guide
- **Token Generation** - Bot and App tokens

📋 **See [Slack_Bot_Setup_Reference.md](Slack_Bot_Setup_Reference.md) for complete setup instructions**

### Environment Variables

```env
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token
DATABASE_URL=postgresql://slack_user:your_password@localhost:5432/slack_database

# RAG Pipeline Configuration (Optional)
RAG_BASIC_URL=https://your-rag-api-endpoint.com/api
RAG_API_KEY=your-rag-api-key-here
```

**RAG Pipeline:** The bot includes a `RAGClient` class for sending data to a RAG (Retrieval-Augmented Generation) pipeline. Configure `RAG_BASIC_URL` and `RAG_API_KEY` if you have a RAG service.

## 🚀 Usage

### Running the Bot

The bot supports **Socket Mode** for real-time events and an **Interactive CLI** for data operations:

```bash
python app.py
```

This starts:

- ✅ **Socket Mode Handler** - Real-time Slack events (messages, reactions, user changes)
- ✅ **Interactive CLI** - Data operations and database queries

### Features

**Real-time Event Handling (Socket Mode):**

- Automatically captures and stores new messages
- Tracks message edits and deletions
- Monitors reactions (added/removed)
- Syncs user changes and new team members
- Handles direct messages and mentions

**Interactive CLI Commands:**

#### Data Fetching

- `fetch <channelId>` - Fetch all messages from a Slack channel (API)
- `thread <threadTs>` - Fetch a full thread from Slack
- `user <userId>` - Fetch user info from Slack
- `users` - Fetch all users from Slack workspace
- `profile <userId>` - Fetch detailed user profile
- `lookup <email>` - Look up a user by email

#### Database Sync

- `sync_all` - Sync all users and channels to database
- `sync <channelId>` - Sync specific channel data to database
- `sync_users` - Sync all workspace users to database

#### Database Queries

- `get_db <channelId>` - Export channel messages from DB
- `search <query>` - Search messages in database
- `user_db <userId>` - Export user's messages from DB
- `thread_db <threadTs>` - Export thread messages from DB

#### Control

- `exit` | `q` | `quit` - Exit the program

## 📊 Database Schema

The bot uses **PostgreSQL** with **Prisma ORM** for data management:

### Models

- **Message** - Slack messages with threading support
- **User** - Workspace members and bots
- **Channel** - Channels with metadata
- **Reaction** - Message reactions
- **File** - File attachments

### Key Features

- ✅ Message threading with parent-child relationships
- ✅ User and channel foreign key relationships
- ✅ Automatic timestamp conversion (Unix ms → DateTime)
- ✅ Comprehensive indexing for performance
- ✅ Real-time data synchronization

## 🔧 Advanced Configuration

### Socket Mode vs HTTP Mode

The bot uses **Socket Mode** by default (no public URL required). To use HTTP mode instead:

1. Disable Socket Mode in Slack App settings
2. Set up a public webhook URL
3. Update event subscriptions to use the webhook URL

### Database Migrations

After schema changes:

```bash
# Create migration
python -m prisma migrate dev --name migration_name

# Generate Prisma client
python -m prisma generate
```
