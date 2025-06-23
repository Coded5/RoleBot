import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import json

load_dotenv()

handler = logging.FileHandler(filename="botlog.log", encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix='!', intents=intents)

role_list_message_id = None

BOT_DATA_FILE = os.environ['BOT_DATA_FILE']

bot_state = {
        'list_message_id': 0,
    'roles': []
}

def update_json():
    global bot_state

    with open(BOT_DATA_FILE, "w") as file:
        json.dump(bot_state, file, indent=4)

@bot.event
async def on_ready():
    global bot_state

    print(f"Logged in as {bot.user.name}")
    try:
        with open(BOT_DATA_FILE, "r") as file:
            bot_state = json.load(file)
    except FileNotFoundError:
        pass

    print(bot_state)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # await message.channel.send(f"Hello, {message.author.mention}")
    await bot.process_commands(message)

@bot.command()
@commands.has_permissions(administrator=True)
async def hello(ctx):
    await ctx.send(f"Hello, {ctx.author.mention}")

@bot.command(name="create_role")
@commands.has_permissions(administrator=True)
async def create_role(ctx, emoji: str, *, name: str):
    global bot_state

    role_name = f"{name}"
    
    # Check if role already exists
    if discord.utils.get(ctx.guild.roles, name=role_name):

        names = [role['name'] for role in bot_state['roles']]

        if role_name not in names:
            bot_state['roles'].append({
                'name': role_name,
                'emoji': emoji
            })
            update_json()

            await ctx.send(f"✅ Role '{role_name}' has been binded to {emoji}")
            return

        await ctx.send(f"❗ A role named '{role_name}' already exists.")
        return

    try:
        new_role = await ctx.guild.create_role(name=role_name)

        bot_state['roles'].append({
            'name': role_name,
            'emoji': emoji,
            'id': new_role.id
        })

        update_json()

        await ctx.send(f"✅ Role '{new_role.name}' created successfully.")
    except discord.Forbidden:
        await ctx.send("🚫 I don't have permission to create roles.")
    except Exception as e:
        await ctx.send(f"⚠️ Something went wrong: `{e}`")

@bot.command(name="list_roles")
@commands.has_permissions(administrator=True)
async def list_roles(ctx, channel: discord.TextChannel):
    global bot_state

    # Exclude @everyone role
    # role_list = [role.name for role in ctx.guild.roles if role.name != "@everyone"]

    role_list = [(role['name'], role['emoji']) for role in bot_state['roles']]

    if not role_list:
        await channel.send("There are no roles in this server.")
        return

    # Build the role list message
    roles_text = "**Server Roles:**\n" + "\n".join(f"- {emoji} {name}" for (name, emoji) in role_list)

    try:
        msg = await channel.send(roles_text)
        bot_state['list_message_id'] = msg.id

        print(f"Message id: {msg.id}")

        for (_, emoji) in role_list:
            print(emoji)
            await msg.add_reaction(emoji)

        print(role_list_message_id)

        update_json()

        await ctx.send(f"✅ Sent role list to {channel.mention}")
    except discord.Forbidden:
        await ctx.send("🚫 I don't have permission to send messages in that channel.")
    except Exception as e:
        print(f"{e}")
        await ctx.send(f"⚠️ An error occurred: `{e}`")

@bot.event
async def on_reaction_add(reaction, user):
    global bot_state

    # Ignore bot reactions
    if user.bot:
        return

    print(f"Reaction from {user.name}")
    print(f"Reacted to {reaction.message.id}")

    # Only respond if the reaction is on the correct message
    if reaction.message.id == bot_state['list_message_id']:
        print(f"Processing role")
        guild = reaction.message.guild
        member = guild.get_member(user.id)

        if member is None:
            print(f"Cannot find user {user.name}")
            return

        emoji = reaction.emoji
        role_id = None

        for role in bot_state['roles']:
            print(role)
            if role['emoji'] == emoji:
                role_id = role['id']
                break

        role = guild.get_role(role_id)
        if role is None:
            print(f"Invalid role {role_id}")
            return

        try:
            await member.add_roles(role)
        except discord.Forbidden:
            print("Missing permission to add roles.")

        await reaction.message.channel.send(
            f"{user.mention} reacted with {reaction.emoji} on the role list!"
        )
        await user

@bot.event
async def on_guild_role_delete(role: discord.Role):
    role_list = [(role['name'], role['emoji']) for role in bot_state['roles']]
    
    print(f"{role.name} Remove")

    for (i, r) in enumerate(bot_state['roles']):
        if r['name'] == role.name:
            bot_state['roles'].pop(i)
            break

    print(bot_state)
    update_json()


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("🚫 You don't have permission to use this command.")
    else:
        raise error  # Let other errors bubble up

token = os.environ["DISCORD_TOKEN"]

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
