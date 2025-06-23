# RoleBot

A very simple reaction role discord bot made with discord.py

## Installtion

### Prerequisite
  * Python and Virtual environment


Just clone the repository and create the virtual environment then use pip to install the required packages and just run the script
```
git clone https://github.com/Coded5/RoleBot.git
cd RoleBot
virtualenv ./venv
pip install -r requirements.txt
```

Next, you need to provide the discord bot token and bot data json in your .env file like the following:
```
DISCORD_TOKEN=<Your token here>
BOT_DATA_FILE=path-to-your-data.json
```
**Note that your must discord bot have member intent and content intent enable in Privileged Gateway Intents**


## Usage

### Commands

All the command are for configuring roles and channels which require the user to have administrator privilege

#### !create_role <emoji> <role_name>
This command will bind the role (if doesn't exists will automatically be created) to the given emoji, the given emoji will be use for reaction

#### !set_log_channel #your-channel
This will set the log channel for the bot. It will send message of granting or removing roles to members. The bot must have access to the given channel

#### !list_roles #your-channel
This command will make the bot send the reaction roles message to the given channel and react to the message. Member can react to the given reaction and the role will be granted. The must have access to the given channel
