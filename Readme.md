# Slack Message Scraping Bot

A Slack bot for retrieving and managing Slack workspace messages.

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

### Environment Variables

```env
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token
DATABASE_URL=postgresql://slack_user:your_password@localhost:5432/slack_database
```

### Required Slack App Permissions

- `channels:history` - Read message history
- `users:read` - View people in a workspace

## 🚀 Usage

### Interactive CLI

```bash
python app.py
```

### Available Commands

- `fetch <channelId>` - Fetch all messages from a Slack channel (API)
- `sync <channelId>` - Sync all users and messages from Slack to DB
- `sync_users` - Sync all users to DB
- `get_db <channelId>` - Export channel messages from DB to `ref/db_messages.json`
- `search <query>` - Search messages in DB and export to `ref/search_results.json`
- `user_db <userId>` - Export a user's messages from DB to `ref/user_messages_db.json`
- `thread_db <threadTs>` - Export a thread's messages from DB to `ref/thread_messages_db.json`
- `thread <threadTs>` - Fetch a full thread from Slack and export to `ref/thread_messages.json`
- `user <userId>` - Fetch user info from Slack and export to `ref/user_info.json`
- `users` - Fetch all users from Slack and export to `ref/all_users.json`
- `profile <userId>` - Fetch user profile from Slack and export to `ref/user_profile.json`
- `lookup <email>` - Look up a user by email and export to `ref/user_lookup.json`
- `exit` | `q` | `quit` - Exit the program
