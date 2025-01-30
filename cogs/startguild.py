import discord
from discord.ext import commands
from collections import defaultdict
from datetime import datetime, timedelta
import asyncio
from config import GUILD_ID, PING_DEF_CHANNEL_ID, ALERTE_DEF_CHANNEL_ID, get_guild_emojis_roles
from views import GuildPingView

class StartGuildCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.cooldowns = {}  # Track cooldowns for guilds
        self.ping_history = defaultdict(list)  # Track ping history
        self.member_counts = {}  # Track member counts for roles

    async def update_member_counts(self):
        """Update active member counts for each guild role."""
        guild = self.bot.get_guild(GUILD_ID)
        if guild:
            for role in guild.roles:
                if role.name.startswith("DEF"):  # Assuming guild roles start with "DEF"
                    self.member_counts[role.name] = len(role.members)

    def add_ping_record(self, guild_name: str, author_id: int):
        """Record a ping event."""
        timestamp = datetime.now()
        self.ping_history[guild_name].append({
            'author_id': author_id,
            'timestamp': timestamp
        })
        # Keep only the last 100 pings
        self.ping_history[guild_name] = self.ping_history[guild_name][-100:]

    def get_ping_stats(self, guild_name: str) -> dict:
        """Calculate ping statistics for the last 24 hours."""
        now = datetime.now()
        day_ago = now - timedelta(days=1)

        recent_pings = [
            ping for ping in self.ping_history[guild_name]
            if ping['timestamp'] > day_ago
        ]
        unique_users = len(set(ping['author_id'] for ping in recent_pings))

        return {
            'total_24h': len(recent_pings),
            'unique_users_24h': unique_users,
            'member_count': self.member_counts.get(guild_name, 0)
        }

    async def ensure_panel(self):
        """
        Ensures that the panel for the alert system is updated or created.
        """
        await self.update_member_counts()

        guild = self.bot.get_guild(GUILD_ID)
        if not guild:
            print("⚠️ Guild not found. Check the GUILD_ID in your configuration.")
            return

        channel = guild.get_channel(PING_DEF_CHANNEL_ID)
        if not channel:
            print("⚠️ Ping definition channel not found. Check the PING_DEF_CHANNEL_ID in your configuration.")
            return

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
            color=discord.Color.blurple()
        )
        embed.set_footer(
            text="Alliance START | Alert System",
            icon_url="https://cdn.discordapp.com/embed/avatars/0.png"
        )   
        
        # Add statistics to the embed
        for guild_name in self.member_counts.keys():
            stats = self.get_ping_stats(guild_name)
            embed.add_field(
                name=f"{guild_name} Stats",
                value=f"👥 Membres: {stats['member_count']}\n"
                      f"🔔 Pings (24h): {stats['total_24h']}\n"
                      f"👤 Utilisateurs uniques: {stats['unique_users_24h']}",
                inline=True
            )

        async for message in channel.history(limit=50):
            if message.pinned:
                await message.edit(embed=embed, view=view)
                print("✅ Panel updated successfully.")
                return

        new_message = await channel.send(embed=embed, view=view)
        await new_message.pin()
        print("✅ Panel created and pinned successfully.")

    async def handle_ping(self, guild_name):
        """Handle the ping functionality with a cooldown."""
        if self.cooldowns.get(guild_name):
            return False  # Guild is on cooldown

        self.cooldowns[guild_name] = True
        await asyncio.sleep(10)  # Cooldown interval (10 seconds)
        self.cooldowns[guild_name] = False
        return True

    @commands.command(name="ping_guild")
    async def ping_guild(self, ctx, guild_name: str):
        """
        Command to ping a guild with statistics and cooldown.
        """
        guild = self.bot.get_guild(GUILD_ID)
        if not guild:
            await ctx.send("⚠️ Guild not found. Check the GUILD_ID in your configuration.")
            return

        if not await self.handle_ping(guild_name):
            await ctx.send(f"⏳ Veuillez attendre avant de ping à nouveau la guilde {guild_name}.")
            return

        self.add_ping_record(guild_name, ctx.author.id)
        await self.ensure_panel()  # Update panel with new stats

        stats = self.get_ping_stats(guild_name)
        await ctx.send(
            f"✅ La guilde {guild_name} a été pingée !\n"
            f"📊 C'est le {stats['total_24h']}e ping aujourd'hui."
        )

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Event listener triggered when the bot is ready.
        """
        await self.ensure_panel()
        guild = self.bot.get_guild(GUILD_ID)
        if guild:
            alert_channel = guild.get_channel(ALERTE_DEF_CHANNEL_ID)
            if alert_channel:
                await alert_channel.set_permissions(
                    guild.default_role, send_messages=False, add_reactions=False
                )
                print("✅ Alert channel permissions updated.")
        print("🚀 Bot is ready and operational.")


async def setup(bot: commands.Bot):
    """Setup function to add the StartGuildCog to the bot."""
    await bot.add_cog(StartGuildCog(bot))
