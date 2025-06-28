import discord
from discord.ext import commands

class ChannelsCog(commands.Cog):
    def __init__(self, bot, bot_state, update_json_func):
        self.bot = bot
        self.bot_state = bot_state
        self.update_json = update_json_func
        # Store selected categories per user per guild
        self.selected_categories = {}  # {guild_id: {user_id: category_id}}

    def get_selected_category(self, guild_id, user_id):
        """Get the currently selected category for a user in a guild"""
        if guild_id not in self.selected_categories:
            return None
        return self.selected_categories[guild_id].get(user_id)

    def set_selected_category(self, guild_id, user_id, category_id):
        """Set the selected category for a user in a guild"""
        if guild_id not in self.selected_categories:
            self.selected_categories[guild_id] = {}
        self.selected_categories[guild_id][user_id] = category_id

    def clear_selected_category(self, guild_id, user_id):
        """Clear the selected category for a user in a guild"""
        if guild_id in self.selected_categories and user_id in self.selected_categories[guild_id]:
            del self.selected_categories[guild_id][user_id]

    # Category Selection Commands
    @commands.command(name="select_category")
    @commands.has_permissions(administrator=True)
    async def select_category(self, ctx, *, category_name: str = None):
        """Select a category to work with. Use without arguments to see available categories."""
        if not category_name:
            # Show available categories
            categories = ctx.guild.categories
            if not categories:
                await ctx.send("No categories found in this server.")
                return

            embed = discord.Embed(title="📁 Available Categories", color=0x3498db)
            embed.description = "Use `!select_category <category_name>` to select one"
            
            for i, category in enumerate(categories, 1):
                channel_count = len(category.channels)
                embed.add_field(
                    name=f"{i}. {category.name}",
                    value=f"ID: {category.id}\nChannels: {channel_count}",
                    inline=True
                )
            
            await ctx.send(embed=embed)
            return

        # Find category by name (case insensitive)
        category = discord.utils.find(
            lambda c: c.name.lower() == category_name.lower(),
            ctx.guild.categories
        )
        
        if not category:
            await ctx.send(f"❌ Category '{category_name}' not found.")
            return

        self.set_selected_category(ctx.guild.id, ctx.author.id, category.id)
        
        embed = discord.Embed(
            title="✅ Category Selected",
            description=f"Selected category: **{category.name}**",
            color=0x00ff00
        )
        embed.add_field(
            name="Available Commands",
            value="""
            `!create_text <name>` - Create text channel
            `!create_voice <name>` - Create voice channel
            `!list_channels` - List channels in category
            `!delete_channel <name>` - Delete channel
            `!rename_channel <old_name> <new_name>` - Rename channel
            `!clear_selection` - Clear category selection
            """,
            inline=False
        )
        
        await ctx.send(embed=embed)

    @commands.command(name="clear_selection")
    @commands.has_permissions(administrator=True)
    async def clear_selection(self, ctx):
        """Clear the selected category"""
        self.clear_selected_category(ctx.guild.id, ctx.author.id)
        await ctx.send("✅ Category selection cleared.")

    @commands.command(name="current_selection")
    @commands.has_permissions(administrator=True)
    async def current_selection(self, ctx):
        """Show the currently selected category"""
        category_id = self.get_selected_category(ctx.guild.id, ctx.author.id)
        if not category_id:
            await ctx.send("❌ No category selected. Use `!select_category` to select one.")
            return
        
        category = ctx.guild.get_channel(category_id)
        if not category:
            self.clear_selected_category(ctx.guild.id, ctx.author.id)
            await ctx.send("❌ Selected category no longer exists. Selection cleared.")
            return
        
        embed = discord.Embed(
            title="📁 Current Selection",
            description=f"Selected category: **{category.name}**",
            color=0x3498db
        )
        embed.add_field(
            name="Channels in Category",
            value=str(len(category.channels)) if category.channels else "0",
            inline=True
        )
        
        await ctx.send(embed=embed)

    # Channel Operations (require selected category)
    @commands.command(name="create_text")
    @commands.has_permissions(administrator=True)
    async def create_text_in_selected(self, ctx, *, name: str):
        """Create a text channel in the selected category"""
        category_id = self.get_selected_category(ctx.guild.id, ctx.author.id)
        if not category_id:
            await ctx.send("❌ No category selected. Use `!select_category` first.")
            return
        
        category = ctx.guild.get_channel(category_id)
        if not category:
            self.clear_selected_category(ctx.guild.id, ctx.author.id)
            await ctx.send("❌ Selected category no longer exists. Please select a new category.")
            return

        try:
            channel = await category.create_text_channel(name)
            await ctx.send(f"✅ Text channel '{channel.name}' created in '{category.name}'.")
        except discord.Forbidden:
            await ctx.send("🚫 I don't have permission to create channels.")
        except Exception as e:
            await ctx.send(f"⚠️ Something went wrong: `{e}`")

    @commands.command(name="create_voice")
    @commands.has_permissions(administrator=True)
    async def create_voice_in_selected(self, ctx, *, name: str):
        """Create a voice channel in the selected category"""
        category_id = self.get_selected_category(ctx.guild.id, ctx.author.id)
        if not category_id:
            await ctx.send("❌ No category selected. Use `!select_category` first.")
            return
        
        category = ctx.guild.get_channel(category_id)
        if not category:
            self.clear_selected_category(ctx.guild.id, ctx.author.id)
            await ctx.send("❌ Selected category no longer exists. Please select a new category.")
            return

        try:
            channel = await category.create_voice_channel(name)
            await ctx.send(f"✅ Voice channel '{channel.name}' created in '{category.name}'.")
        except discord.Forbidden:
            await ctx.send("🚫 I don't have permission to create channels.")
        except Exception as e:
            await ctx.send(f"⚠️ Something went wrong: `{e}`")

    @commands.command(name="list_channels")
    @commands.has_permissions(administrator=True)
    async def list_channels_in_selected(self, ctx):
        """List all channels in the selected category"""
        category_id = self.get_selected_category(ctx.guild.id, ctx.author.id)
        if not category_id:
            await ctx.send("❌ No category selected. Use `!select_category` first.")
            return
        
        category = ctx.guild.get_channel(category_id)
        if not category:
            self.clear_selected_category(ctx.guild.id, ctx.author.id)
            await ctx.send("❌ Selected category no longer exists. Please select a new category.")
            return

        if not category.channels:
            await ctx.send(f"📁 Category '{category.name}' has no channels.")
            return

        embed = discord.Embed(
            title=f"📁 Channels in '{category.name}'",
            color=0x3498db
        )
        
        text_channels = [c for c in category.channels if isinstance(c, discord.TextChannel)]
        voice_channels = [c for c in category.channels if isinstance(c, discord.VoiceChannel)]
        
        if text_channels:
            text_list = "\n".join([f"📝 {ch.name}" for ch in text_channels])
            embed.add_field(name="Text Channels", value=text_list, inline=True)
        
        if voice_channels:
            voice_list = "\n".join([f"🔊 {ch.name}" for ch in voice_channels])
            embed.add_field(name="Voice Channels", value=voice_list, inline=True)
        
        await ctx.send(embed=embed)

    @commands.command(name="delete_channel")
    @commands.has_permissions(administrator=True)
    async def delete_channel_in_selected(self, ctx, *, channel_name: str):
        """Delete a channel in the selected category"""
        category_id = self.get_selected_category(ctx.guild.id, ctx.author.id)
        if not category_id:
            await ctx.send("❌ No category selected. Use `!select_category` first.")
            return
        
        category = ctx.guild.get_channel(category_id)
        if not category:
            self.clear_selected_category(ctx.guild.id, ctx.author.id)
            await ctx.send("❌ Selected category no longer exists. Please select a new category.")
            return

        # Find channel by name in the category
        channel = discord.utils.find(
            lambda c: c.name.lower() == channel_name.lower(),
            category.channels
        )
        
        if not channel:
            await ctx.send(f"❌ Channel '{channel_name}' not found in '{category.name}'.")
            return

        try:
            await channel.delete()
            await ctx.send(f"✅ Channel '{channel_name}' deleted from '{category.name}'.")
        except discord.Forbidden:
            await ctx.send("🚫 I don't have permission to delete channels.")
        except Exception as e:
            await ctx.send(f"⚠️ Something went wrong: `{e}`")

    @commands.command(name="rename_channel")
    @commands.has_permissions(administrator=True)
    async def rename_channel_in_selected(self, ctx, old_name: str, *, new_name: str):
        """Rename a channel in the selected category"""
        category_id = self.get_selected_category(ctx.guild.id, ctx.author.id)
        if not category_id:
            await ctx.send("❌ No category selected. Use `!select_category` first.")
            return
        
        category = ctx.guild.get_channel(category_id)
        if not category:
            self.clear_selected_category(ctx.guild.id, ctx.author.id)
            await ctx.send("❌ Selected category no longer exists. Please select a new category.")
            return

        # Find channel by name in the category
        channel = discord.utils.find(
            lambda c: c.name.lower() == old_name.lower(),
            category.channels
        )
        
        if not channel:
            await ctx.send(f"❌ Channel '{old_name}' not found in '{category.name}'.")
            return

        try:
            await channel.edit(name=new_name)
            await ctx.send(f"✅ Channel '{old_name}' renamed to '{new_name}' in '{category.name}'.")
        except discord.Forbidden:
            await ctx.send("🚫 I don't have permission to edit channels.")
        except Exception as e:
            await ctx.send(f"⚠️ Something went wrong: `{e}`")

    @commands.command(name="move_channel_to_selected")
    @commands.has_permissions(administrator=True)
    async def move_channel_to_selected(self, ctx, *, channel_name: str):
        """Move a channel from anywhere in the server to the selected category"""
        category_id = self.get_selected_category(ctx.guild.id, ctx.author.id)
        if not category_id:
            await ctx.send("❌ No category selected. Use `!select_category` first.")
            return
        
        category = ctx.guild.get_channel(category_id)
        if not category:
            self.clear_selected_category(ctx.guild.id, ctx.author.id)
            await ctx.send("❌ Selected category no longer exists. Please select a new category.")
            return

        # Find channel by name in the entire server
        channel = discord.utils.find(
            lambda c: c.name.lower() == channel_name.lower() and isinstance(c, (discord.TextChannel, discord.VoiceChannel)),
            ctx.guild.channels
        )
        
        if not channel:
            await ctx.send(f"❌ Channel '{channel_name}' not found in the server.")
            return

        try:
            await channel.edit(category=category)
            await ctx.send(f"✅ Channel '{channel.name}' moved to '{category.name}'.")
        except discord.Forbidden:
            await ctx.send("🚫 I don't have permission to edit channels.")
        except Exception as e:
            await ctx.send(f"⚠️ Something went wrong: `{e}`")

    # Original category management commands (kept for compatibility)
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

    # Legacy commands for backward compatibility
    @commands.command(name="create_text_channel")
    @commands.has_permissions(administrator=True)
    async def create_text_channel(self, ctx, category: discord.CategoryChannel, *, name: str):
        """Create a text channel in specified category (legacy command)"""
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
        """Create a voice channel in specified category (legacy command)"""
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
        """Move a channel to a different category (legacy command)"""
        try:
            await channel.edit(category=category)
            await ctx.send(f"✅ Channel '{channel.name}' moved to '{category.name}'.")
        except discord.Forbidden:
            await ctx.send("🚫 I don't have permission to edit channels.")
        except Exception as e:
            await ctx.send(f"⚠️ Something went wrong: `{e}`")

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
    await bot.add_cog(ChannelsCog(bot, None, None))