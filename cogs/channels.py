import discord
from discord.ext import commands

class ChannelsCog(commands.Cog):
    def __init__(self, bot, bot_state, update_json_func):
        self.bot = bot
        self.bot_state = bot_state
        self.update_json = update_json_func

    @commands.command(name="create_category")
    @commands.has_permissions(administrator=True)
    async def create_category(self, ctx, *, name: str):
        """Create a new category"""
        try:
            category = await ctx.guild.create_category(name)
            await ctx.send(f"✅ Category '{category.name}' created successfully.")
        except discord.Forbidden:
            await ctx.send("🚫 I don't have permission to create categories.")
        except Exception as e:
            await ctx.send(f"⚠️ Something went wrong: `{e}`")

    @commands.command(name="duplicate_category")
    @commands.has_permissions(administrator=True)
    async def duplicate_category(self, ctx, source_category: discord.CategoryChannel, *, new_name: str):
        """Duplicate a category with all its channels and permissions"""
        try:
            # Create new category with same permissions
            new_category = await ctx.guild.create_category(
                new_name,
                overwrites=source_category.overwrites,
                position=source_category.position + 1
            )

            # Copy all channels from source category
            for channel in source_category.channels:
                if isinstance(channel, discord.TextChannel):
                    await new_category.create_text_channel(
                        channel.name,
                        overwrites=channel.overwrites,
                        topic=channel.topic,
                        slowmode_delay=channel.slowmode_delay,
                        nsfw=channel.nsfw
                    )
                elif isinstance(channel, discord.VoiceChannel):
                    await new_category.create_voice_channel(
                        channel.name,
                        overwrites=channel.overwrites,
                        bitrate=channel.bitrate,
                        user_limit=channel.user_limit
                    )

            await ctx.send(f"✅ Category '{source_category.name}' duplicated as '{new_name}' with all channels and permissions.")
        
        except discord.Forbidden:
            await ctx.send("🚫 I don't have permission to create categories or channels.")
        except Exception as e:
            await ctx.send(f"⚠️ Something went wrong: `{e}`")

    @commands.command(name="create_text_channel")
    @commands.has_permissions(administrator=True)
    async def create_text_channel(self, ctx, category: discord.CategoryChannel, *, name: str):
        """Create a text channel in specified category"""
        try:
            channel = await category.create_text_channel(name)
            await ctx.send(f"✅ Text channel '{channel.name}' created in '{category.name}'.")
        except discord.Forbidden:
            await ctx.send("🚫 I don't have permission to create channels.")
        except Exception as e:
            await ctx.send(f"⚠️ Something went wrong: `{e}`")

    @commands.command(name="create_voice_channel")
    @commands.has_permissions(administrator=True)
    async def create_voice_channel(self, ctx, category: discord.CategoryChannel, *, name: str):
        """Create a voice channel in specified category"""
        try:
            channel = await category.create_voice_channel(name)
            await ctx.send(f"✅ Voice channel '{channel.name}' created in '{category.name}'.")
        except discord.Forbidden:
            await ctx.send("🚫 I don't have permission to create channels.")
        except Exception as e:
            await ctx.send(f"⚠️ Something went wrong: `{e}`")

    @commands.command(name="move_channel")
    @commands.has_permissions(administrator=True)
    async def move_channel(self, ctx, channel: discord.TextChannel, category: discord.CategoryChannel):
        """Move a channel to a different category"""
        try:
            await channel.edit(category=category)
            await ctx.send(f"✅ Channel '{channel.name}' moved to '{category.name}'.")
        except discord.Forbidden:
            await ctx.send("🚫 I don't have permission to edit channels.")
        except Exception as e:
            await ctx.send(f"⚠️ Something went wrong: `{e}`")

    @commands.command(name="delete_category")
    @commands.has_permissions(administrator=True)
    async def delete_category(self, ctx, category: discord.CategoryChannel, confirm: str = None):
        """Delete a category (requires 'confirm' as second argument)"""
        if confirm != "confirm":
            await ctx.send(f"⚠️ This will delete the category '{category.name}' and all its channels. Use `!delete_category {category.id} confirm` to proceed.")
            return

        try:
            # Delete all channels in category first
            for channel in category.channels:
                await channel.delete()
            
            # Delete the category
            await category.delete()
            await ctx.send(f"✅ Category '{category.name}' and all its channels have been deleted.")
        except discord.Forbidden:
            await ctx.send("🚫 I don't have permission to delete categories or channels.")
        except Exception as e:
            await ctx.send(f"⚠️ Something went wrong: `{e}`")

    @commands.command(name="list_categories")
    @commands.has_permissions(administrator=True)
    async def list_categories(self, ctx):
        """List all categories in the server"""
        categories = ctx.guild.categories
        
        if not categories:
            await ctx.send("No categories found in this server.")
            return

        embed = discord.Embed(title="Server Categories", color=0x3498db)
        
        for category in categories:
            channel_count = len(category.channels)
            text_channels = len([c for c in category.channels if isinstance(c, discord.TextChannel)])
            voice_channels = len([c for c in category.channels if isinstance(c, discord.VoiceChannel)])
            
            embed.add_field(
                name=f"📁 {category.name}",
                value=f"ID: {category.id}\nChannels: {channel_count} (📝 {text_channels} text, 🔊 {voice_channels} voice)",
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(name="clone_channel")
    @commands.has_permissions(administrator=True)
    async def clone_channel(self, ctx, channel: discord.TextChannel, *, new_name: str = None):
        """Clone a text channel with all its settings"""
        try:
            clone_name = new_name or f"{channel.name}-clone"
            
            cloned_channel = await channel.clone(name=clone_name)
            await ctx.send(f"✅ Channel '{channel.name}' cloned as '{cloned_channel.name}'.")
        except discord.Forbidden:
            await ctx.send("🚫 I don't have permission to clone channels.")
        except Exception as e:
            await ctx.send(f"⚠️ Something went wrong: `{e}`")

    @commands.command(name="set_channel_topic")
    @commands.has_permissions(administrator=True)
    async def set_channel_topic(self, ctx, channel: discord.TextChannel, *, topic: str):
        """Set the topic for a text channel"""
        try:
            await channel.edit(topic=topic)
            await ctx.send(f"✅ Topic set for '{channel.name}': {topic}")
        except discord.Forbidden:
            await ctx.send("🚫 I don't have permission to edit channels.")
        except Exception as e:
            await ctx.send(f"⚠️ Something went wrong: `{e}`")

async def setup(bot):
    await bot.add_cog(ChannelsCog(bot))