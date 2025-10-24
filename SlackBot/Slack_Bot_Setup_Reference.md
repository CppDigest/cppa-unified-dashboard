## 🧾 Slack Bot Configuration & Permissions Documentation

### **Bot Overview**

This Slack bot provides comprehensive workspace monitoring and interaction capabilities:

#### **Core Features**

- **Channel Management**: Join, list, and monitor public channels
- **Message Handling**: Read message history from channels, threads, DMs, and group DMs
- **Communication**: Send messages and replies to channels, DMs, and group DMs
- **User Interaction**: Respond to mentions (`@bot`) and slash commands (`/help`)
- **File Access**: Read uploaded files and attachments
- **Reactions**: Monitor emoji reactions on messages
- **User Information**: Access basic user profiles and workspace data

#### **Event Monitoring**

The bot receives real-time notifications for:

- New messages posted or edited in channels and DMs
- Message deletions and bulk history changes
- Emoji reactions added or removed
- New members joining the workspace
- User profile updates and changes

---

## ⚙️ **Bot OAuth Scopes**

| **Scope**           | **Purpose / Description**                                                                 |
| ------------------- | ----------------------------------------------------------------------------------------- |
| `app_mentions:read` | Read messages where the bot is mentioned.                                                 |
| `channels:history`  | Read message history from public channels.                                                |
| `channels:join`     | Allow the bot to join public channels.                                                    |
| `channels:read`     | Get list of all public channels and their info.                                           |
| `chat:write`        | Post messages in channels as the bot.                                                     |
| `commands`          | Add shortcuts and/or slash commands that people can use.                                  |
| `files:read`        | Read uploaded files (optional if you want to monitor attachments).                        |
| `im:history`        | Read message history from DMs.                                                            |
| `im:read`           | Access bot's direct message conversations.                                                |
| `im:write`          | Start direct messages with people and send direct messages to users.                      |
| `mpim:history`      | View messages and other content in group direct messages that this bot has been added to. |
| `mpim:read`         | View basic information about group direct messages that this bot has been added to.       |
| `mpim:write`        | Start group direct messages with people.                                                  |
| `reactions:read`    | Read reactions on messages.                                                               |
| `users:read`        | Read basic user profile fields (id, name, display name, etc.).                            |

---

## 📡 **Event Subscriptions**

| **Event Name**          | **Description**                                                   |
| ----------------------- | ----------------------------------------------------------------- |
| `app_mention`           | Subscribe to only the message events that mention your app or bot |
| `im_history_changed`    | Bulk updates were made to a DM's history                          |
| `member_joined_channel` | A user joined a public channel, private channel or MPDM           |
| `member_left_channel`   | A user left a public or private channel                           |
| `message.channels`      | A message was posted to a channel                                 |
| `message.im`            | A message was posted in a direct message channel                  |
| `message.mpim`          | A message was posted in a multiparty direct message channel       |
| `reaction_added`        | A member has added an emoji reaction to an item                   |
| `reaction_removed`      | A member removed an emoji reaction                                |
| `team_join`             | A new member has joined                                           |
| `user_change`           | A member's data has changed                                       |

---

## 🧠 **Implementation Steps**

### 1. **Create Slack App**

- Navigate to the [Slack API Dashboard](https://api.slack.com/apps)
- Click **Create New App** → Select **From scratch**
- Enter your **App Name** and select the target workspace
- Click **Create App**

### 2. **Configure App-Level Token (for Socket Mode)**

- Go to **Basic Information** tab
- Scroll to **App-Level Tokens** section
- Click **Generate Token and Scopes**
- Add the `connections:write` scope
- Save the generated token securely

### 3. **Enable Socket Mode**

- Navigate to **Socket Mode** in the sidebar
- Toggle **Enable Socket Mode** to ON
- This enables real-time event handling without a public URL

### 4. **Configure OAuth Scopes**

- Go to **OAuth & Permissions** tab
- Scroll to **Scopes** → **Bot Token Scopes**
- Add all OAuth scopes listed in the table above
- Click **Add an OAuth Scope** for each required permission

### 5. **Subscribe to Events**

- Navigate to **Event Subscriptions** tab
- Toggle **Enable Events** to ON
- Under **Subscribe to bot events**, add all events listed in the table above
- Click **Save Changes**

### 6. **Create Slash Commands**

- Go to **Slash Commands** tab
- Click **Create New Command**
- Add the `/help` command with appropriate description and usage hint
- Save the command

### 7. **Install App to Workspace**

- Go to **OAuth & Permissions** tab
- Click **Install to Workspace**
- Review permissions and authorize
- Save the **Bot User OAuth Token** (starts with `xoxb-`) for your application

---

## 🔐 **Tokens Needed**

| **Type**                | **Example Prefix** | **Used For**                                     |
| ----------------------- | ------------------ | ------------------------------------------------ |
| **Bot Token**           | `xoxb-...`         | Main bot operations (read/write/chat).           |
| **App Token**           | `xapp-...`         | Required if using Socket Mode.                   |
| _(Optional)_ User Token | `xoxp-...`         | For admin actions like deleting system messages. |
