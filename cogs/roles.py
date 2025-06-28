import discord
from discord.ext import commands

class RolesCog(commands.Cog):
    def __init__(self, bot, bot_state, update_json_func):
        self.bot = bot
        self.bot_state = bot_state
        self.update_json = update_json_func

    @commands.command(name="create_role")
    @commands.has_permissions(administrator=True)
    async def create_role(self, ctx, emoji: str, *, name: str):
        """Create a new role with emoji binding"""
        role_name = f"{name}"
        
        # Check if role already exists
        if discord.utils.get(ctx.guild.roles, name=role_name):
            names = [role['name'] for role in self.bot_state['roles']]

            if role_name not in names:
                self.bot_state['roles'].append({
                    'name': role_name,
                    'emoji': emoji
                })
                self.update_json()
                await ctx.send(f"✅ Role '{role_name}' has been binded to {emoji}")
                return

            await ctx.send(f"❗ A role named '{role_name}' already exists.")
            return

        try:
            new_role = await ctx.guild.create_role(name=role_name)

            self.bot_state['roles'].append({
                'name': role_name,
                'emoji': emoji,
                'id': new_role.id
            })

            self.update_json()
            await ctx.send(f"✅ Role '{new_role.name}' created successfully.")
        except discord.Forbidden:
            await ctx.send("🚫 I don't have permission to create roles.")
        except Exception as e:
            await ctx.send(f"⚠️ Something went wrong: `{e}`")

    @commands.command(name="list_roles")
    @commands.has_permissions(administrator=True)
    async def list_roles(self, ctx, channel: discord.TextChannel):
        """Create a role list message with reactions in specified channel"""
        role_list = [(role['name'], role['emoji']) for role in self.bot_state['roles']]

        if not role_list:
            await channel.send("There are no roles in this server.")
            return

        # Build the role list message
        roles_text = "**Server Roles:**\n" + "\n".join(f"- {emoji} {name}" for (name, emoji) in role_list)

        try:
            msg = await channel.send(roles_text)
            self.bot_state['list_message_id'] = msg.id

            for (_, emoji) in role_list:
                await msg.add_reaction(emoji)

            self.update_json()
            await ctx.send(f"✅ Sent role list to {channel.mention}")
        except discord.Forbidden:
            await ctx.send("🚫 I don't have permission to send messages in that channel.")
        except Exception as e:
            await ctx.send(f"⚠️ An error occurred: `{e}`")

    @commands.command(name="remove_role")
    @commands.has_permissions(administrator=True)
    async def remove_role(self, ctx, *, role_name: str):
        """Remove a role from the server and bot state"""
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        
        if not role:
            await ctx.send(f"❗ Role '{role_name}' not found.")
            return

        try:
            await role.delete()
            await ctx.send(f"✅ Role '{role_name}' deleted successfully.")
        except discord.Forbidden:
            await ctx.send("🚫 I don't have permission to delete roles.")
        except Exception as e:
            await ctx.send(f"⚠️ Something went wrong: `{e}`")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        """Handle role assignment via reactions"""
        # Ignore bot reactions
        if payload.user_id == self.bot.user.id:
            return

        # Only respond if the reaction is on the correct message
        if payload.message_id == self.bot_state['list_message_id']:
            guild = self.bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)

            if member is None:
                return

            emoji = payload.emoji
            emoji_key = (
                f"<{'a' if emoji.animated else ''}:{emoji.name}:{emoji.id}>"
                if emoji.is_custom_emoji() else emoji.name
            )

            role_id = None
            for role in self.bot_state['roles']:
                if role['emoji'] == emoji_key:
                    role_id = role.get('id')
                    break

            if role_id is None:
                return

            role = guild.get_role(role_id)
            if role is None:
                return

            try:
                await member.add_roles(role)
            except discord.Forbidden:
                print("Missing permission to add roles.")
                return

            channel = self.bot.get_channel(self.bot_state['log_channel_id'])
            if channel:
                await channel.send(
                    f"<@{payload.user_id}> reacted with {emoji_key} and received the {role.name} role!"
                )

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        """Handle role removal via reactions"""
        if payload.user_id == self.bot.user.id:
            return

        if payload.message_id == self.bot_state['list_message_id']:
            guild = self.bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)

            if member is None:
                return

            emoji = payload.emoji
            emoji_key = (
                f"<{'a' if emoji.animated else ''}:{emoji.name}:{emoji.id}>"
                if emoji.is_custom_emoji() else emoji.name
            )

            role_id = None
            for role in self.bot_state['roles']:
                if role['emoji'] == emoji_key:
                    role_id = role.get('id')
                    break

            if role_id is None:
                return

            role = guild.get_role(role_id)
            if role is None:
                return

            try:
                await member.remove_roles(role)
            except discord.Forbidden:
                print("Missing permission to remove roles.")
                return

            channel = self.bot.get_channel(self.bot_state['log_channel_id'])
            if channel:
                await channel.send(
                    f"<@{payload.user_id}> removed their {emoji_key} reaction — {role.name} role removed."
                )

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        """Clean up bot state when a role is deleted"""
        for i, r in enumerate(self.bot_state['roles']):
            if r['name'] == role.name:
                self.bot_state['roles'].pop(i)
                break
        
        self.update_json()

async def setup(bot):
    await bot.add_cog(RolesCog(bot))