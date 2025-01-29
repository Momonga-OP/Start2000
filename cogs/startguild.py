from discord.ext import commands
from discord import app_commands
from .database import add_guild, delete_guild, get_all_guilds

class GuildManagementCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="add_guild", description="Add a new guild to the database")
    @app_commands.describe(guild_name="Name of the guild", emoji_id="Emoji ID for the guild", role_id="Role ID for the guild")
    async def add_guild(self, interaction: discord.Interaction, guild_name: str, emoji_id: str, role_id: str):
        try:
            add_guild(guild_name, emoji_id, role_id)
            await interaction.response.send_message(f"✅ Guild '{guild_name}' added successfully!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

    @app_commands.command(name="delete_guild", description="Delete a guild from the database")
    @app_commands.describe(guild_name="Name of the guild to delete")
    async def delete_guild(self, interaction: discord.Interaction, guild_name: str):
        try:
            delete_guild(guild_name)
            await interaction.response.send_message(f"✅ Guild '{guild_name}' deleted successfully!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {e}", ephemeral=True)

    @app_commands.command(name="list_guilds", description="List all guilds in the database")
    async def list_guilds(self, interaction: discord.Interaction):
        guilds = get_all_guilds()
        if not guilds:
            await interaction.response.send_message("No guilds found in the database.", ephemeral=True)
            return

        guild_list = "\n".join([f"{guild[1]} (Emoji: {guild[2]}, Role ID: {guild[3]})" for guild in guilds])
        await interaction.response.send_message(f"**Guilds:**\n{guild_list}", ephemeral=True)

async def setup(bot: commands.Bot):
    """Add the GuildManagementCog to the bot."""
    await bot.add_cog(GuildManagementCog(bot))
