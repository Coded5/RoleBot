# RoleBot

A Discord bot for reaction roles and channel management made with discord.py

## Installation

### Prerequisites

- Python and Virtual environment

Just clone the repository, create the virtual environment, then use pip to install the required packages and run the script:

```bash
git clone https://github.com/Coded5/RoleBot.git
cd RoleBot
virtualenv ./venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Next, provide the Discord bot token and bot data JSON in your `.env` file like the following:

```env
DISCORD_TOKEN=<Your token here>
BOT_DATA_FILE=path-to-your-data.json
```

> **Note:** Your Discord bot must have **Message Content Intent** and **Server Members Intent** enabled in Privileged Gateway Intents.

---

## Features

- **Reaction Roles:** Automatic role assignment/removal via emoji reactions
- **Channel Management:** Create, duplicate, and manage channels and categories
- **Permission Control:** All administrative commands require administrator permissions
- **Logging:** Configurable logging channel for role assignments

---

## Usage

### Commands

> All commands require administrator privileges.

#### Role Management

- `!create_role <emoji> <role_name>` — Bind a role to an emoji for reaction roles  
- `!list_roles #channel` — Send interactive role menu to specified channel  
- `!remove_role <role_name>` — Delete a role from the server  
- `!set_log_channel #channel` — Set channel for role assignment logs  

#### Category Management

- `!create_category <name>` — Create a new category  
- `!duplicate_category <source_category> <new_name>` — Duplicate category with all channels  
- `!delete_category <category> confirm` — Delete category and all channels  
- `!list_categories` — List all server categories  

#### Channel Management

- `!create_text_channel <category> <name>` — Create text channel in category  
- `!create_voice_channel <category> <name>` — Create voice channel in category  
- `!move_channel <channel> <category>` — Move channel to different category  
- `!clone_channel <channel> [new_name]` — Clone a text channel  
- `!set_channel_topic <channel> <topic>` — Set channel topic  

---

## Bot Permissions Required

- Manage Roles
- Manage Channels
- Send Messages
- Add Reactions
- Read Message History
- View Channels

---

## Setup Guide

1. **Set log channel:**  
   `!set_log_channel #bot-logs`
2. **Create roles:**  
   `!create_role 🎮 Gamer`
3. **Deploy role menu:**  
   `!list_roles #roles`
4. Members can now react to get roles