import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import json

# Import cogs
from cogs.roles import RolesCog
from cogs.channels import ChannelsCog

load_dotenv()

# Bot setup
handler = logging.FileHandler(filename="botlog.log", encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Global bot state
BOT_DATA_FILE = os.environ['BOT_DATA_FILE']

bot_state = {
    'log_channel_id': 0,
    'list_message_id': 0,
    'roles': [],
    'categories': []  # For future channel management
}

def update_json():
    """Update the bot state JSON file"""
    global bot_state
    with open(BOT_DATA_FILE, "w") as file:
        json.dump(bot_state, file, indent=4)

def load_bot_state():
    """Load bot state from JSON file"""
    global bot_state
    try:
        with open(BOT_DATA_FILE, "r") as file:
            bot_state = json.load(file)
    except FileNotFoundError:
        pass

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    load_bot_state()
    print(bot_state)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)

@bot.command(name="set_log_channel")
@commands.has_permissions(administrator=True)
async def set_log_channel(ctx, channel: discord.TextChannel):
    """Set the logging channel for the bot"""
    global bot_state
    bot_state['log_channel_id'] = channel.id
    c = bot.get_channel(bot_state['log_channel_id'])
    if c is not None and isinstance(c, discord.TextChannel):
        await c.send("I will log to this channel from now on")
    update_json()
    await ctx.send(f"✅ Log channel set to {channel.mention}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("🚫 You don't have permission to use this command.")
    else:
        raise error

async def main():
    """Main function to setup and run the bot"""
    # Add cogs
    await bot.add_cog(RolesCog(bot, bot_state, update_json))
    await bot.add_cog(ChannelsCog(bot, bot_state, update_json))
    
    # Run the bot
    token = os.environ["DISCORD_TOKEN"]
    await bot.start(token)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())