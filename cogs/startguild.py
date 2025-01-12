import discord
from discord.ext import commands
import asyncio
from .config import GUILD_ID, PING_DEF_CHANNEL_ID, ALERTE_DEF_CHANNEL_ID
from .views import GuildPingView

class StartGuildCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.cooldowns = {}  # Track cooldowns for guilds

    async def ensure_panel(self):
        """
        Ensures that the panel for the alert system is updated or created.
        """
        # Fetch the guild
        guild = self.bot.get_guild(GUILD_ID)
        if not guild:
            print("⚠️ Guild not found. Check the GUILD_ID in your configuration.")
            return

        # Fetch the designated channel for ping definitions
        channel = guild.get_channel(PING_DEF_CHANNEL_ID)
        if not channel:
            print("⚠️ Ping definition channel not found. Check the PING_DEF_CHANNEL_ID in your configuration.")
            return

        # Create the interactive view and the embed
        view = GuildPingView(self.bot)
        embed = discord.Embed(
            title="🎯 Panneau d'Alerte DEF",
            description=(
                "Bienvenue sur le **Panneau d'Alerte Défense** !\n\n"
                "Utilisez les boutons ci-dessous pour envoyer une alerte à votre guilde. "
                "Cliquez simplement sur le bouton correspondant pour notifier ses membres.\n\n"
                "**📋 Instructions :**\n"
                "1️⃣ Cliquez sur le bouton correspondant à votre guilde.\n"
                "2️⃣ Suivez les mises à jour dans le canal d'alerte.\n"
                "3️⃣ Ajoutez des notes si nécessaire.\n\n"
                "⬇️ **Guildes Disponibles** ⬇️"
            ),
            color=discord.Color.blurple()  # Using blurple for a modern, Discord-friendly color.
        )
        embed.set_footer(text="Alliance START | Alert System", icon_url="https://github.com/Momonga-Og/Start2000/blob/cc0b2ecde19684cb4196c2dab3a1b490439b14ae/standard%20(1).gif")

        # Check for an existing pinned message to update it
        async for message in channel.history(limit=50):
            if message.pinned:
                await message.edit(embed=embed, view=view)
                print("✅ Panel updated successfully.")
                return

        # Create and pin a new message if none exist
        new_message = await channel.send(embed=embed, view=view)
        await new_message.pin()
        print("✅ Panel created and pinned successfully.")

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Event listener triggered when the bot is ready. Ensures the alert panel and updates permissions.
        """
        await self.ensure_panel()

        # Fetch the guild and alert channel
        guild = self.bot.get_guild(GUILD_ID)
        if not guild:
            print("⚠️ Guild not found. Check the GUILD_ID in your configuration.")
            return

        alert_channel = guild.get_channel(ALERTE_DEF_CHANNEL_ID)
        if alert_channel:
            # Update alert channel permissions to restrict sending and reactions
            await alert_channel.set_permissions(
                guild.default_role, send_messages=False, add_reactions=False
            )
            print("✅ Alert channel permissions updated.")

        print("🚀 Bot is ready and operational.")

    async def handle_ping(self, guild_name):
        """
        Handle the ping functionality with a cooldown.
        """
        if self.cooldowns.get(guild_name):
            return False  # Guild is on cooldown

        self.cooldowns[guild_name] = True
        await asyncio.sleep(10)  # Cooldown interval (10 seconds)
        self.cooldowns[guild_name] = False
        return True

    @commands.command(name="ping_guild")
    async def ping_guild(self, ctx, guild_name: str):
        """
        Command to ping a guild with a cooldown.
        """
        guild = self.bot.get_guild(GUILD_ID)
        if not guild:
            await ctx.send("⚠️ Guild not found. Check the GUILD_ID in your configuration.")
            return

        # Check and enforce the cooldown
        if not await self.handle_ping(guild_name):
            await ctx.send(f"⏳ Veuillez attendre avant de ping à nouveau la guilde {guild_name}.")
            return

        # Logic for sending a ping notification (to be implemented)
        await ctx.send(f"✅ La guilde {guild_name} a été pingée !")

# Async function to add the cog to the bot
async def setup(bot: commands.Bot):
    """
    Setup function to add the StartGuildCog to the bot.
    """
    await bot.add_cog(StartGuildCog(bot))
