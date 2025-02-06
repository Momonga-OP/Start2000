import discord
from discord.ext import commands
from collections import defaultdict
from datetime import datetime, timedelta
import asyncio
from typing import Optional
from .config import GUILD_ID, PING_DEF_CHANNEL_ID, ALERTE_DEF_CHANNEL_ID
from .views import GuildPingView


class StartGuildCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        """
        Initialize the cog with necessary attributes.
        """
        self.bot = bot
        self.cooldowns = {}  # Track cooldowns for guild pings
        self.ping_history = defaultdict(list)  # Store ping history per guild
        self.member_counts = {}  # Track active member counts per guild
        self.panel_message: Optional[discord.Message] = None  # Reference to the panel message

    @staticmethod
    def create_progress_bar(percentage: float, length: int = 10) -> str:
        """
        Create a progress bar string based on the given percentage.
        """
        filled = '▰' * int(round(percentage * length))
        empty = '▱' * (length - len(filled))
        return f"{filled}{empty} {int(percentage * 100)}%"

    async def update_member_counts(self):
        """
        Update the count of active members in each guild role.
        """
        guild = self.bot.get_guild(GUILD_ID)
        if not guild:
            return

        await guild.chunk()  # Ensure all members are loaded
        self.member_counts.clear()  # Clear previous counts to avoid stale data

        for role in guild.roles:
            if role.name.startswith("DEF"):
                self.member_counts[role.name] = sum(
                    1 for member in role.members
                    if not member.bot and member.raw_status != 'offline'
                )

    def add_ping_record(self, guild_name: str, author_id: int):
        """
        Record a new ping event for the specified guild.
        """
        timestamp = datetime.now()
        self.ping_history[guild_name].append({
            'author_id': author_id,
            'timestamp': timestamp
        })

        # Keep only the last 100 records within the last 7 days
        cutoff = datetime.now() - timedelta(days=7)
        self.ping_history[guild_name] = [
            ping for ping in self.ping_history[guild_name]
            if ping['timestamp'] > cutoff
        ][-100:]

    def get_ping_stats(self, guild_name: str) -> dict:
        """
        Calculate statistics for the specified guild's ping history.
        """
        now = datetime.now()
        periods = {
            '24h': now - timedelta(hours=24),
            '7j': now - timedelta(days=7)
        }
        stats = {'member_count': self.member_counts.get(guild_name, 0)}

        for period, cutoff in periods.items():
            pings = [p for p in self.ping_history[guild_name] if p['timestamp'] > cutoff]
            stats.update({
                f'total_{period}': len(pings),
                f'unique_{period}': len({p['author_id'] for p in pings}),
                f'activite_{period}': min(100, len(pings) * 2)
            })

        return stats

    async def create_panel_embed(self) -> discord.Embed:
        """
        Generate the embed for the guild alert panel.
        """
        await self.update_member_counts()

        total_connected = sum(self.member_counts.values())

        embed = discord.Embed(
            title="🛡️ Panneau d'Alerte Défense",
            color=discord.Color.gold(),
            timestamp=datetime.now()
        )

        embed.set_author(
            name="Système d'Alerte START",
            icon_url="https://github.com/Momonga-OP/Start2000/blob/main/35_35-0%20(2).png?raw=true"
        )

        embed.description = (
            "```diff\n+ SYSTÈME D'ALERTE GUILDE [v2.7.0]\n```\n"
            "**📋 Instructions :**\n"
            "1️⃣ Cliquez sur le bouton de votre guilde\n"
            "2️⃣ Suivez les mises à jour dans #║╟➢📯alertes-def \n"
            "3️⃣ Ajoutez des notes si nécessaire\n\n"
            f"👥 Membres connectés: {total_connected}\n"
            "```ansi\n[2;34m[!] Statut système: [0m[2;32mOPÉRATIONNEL[0m```"
        )

        for guild_name, count in self.member_counts.items():
            stats = self.get_ping_stats(guild_name)
            activity = self.create_progress_bar(stats['activite_24h'] / 100)

            embed.add_field(
                name=f"📌 {guild_name}",
                value=(
                    f"```prolog\n"
                    f"[🟢 Connectés] {count}\n"
                    f"[📨 Pings 24h] {stats['total_24h']}\n"
                    f"[⏱ Cooldown] {'🟠 Actif' if self.cooldowns.get(guild_name) else '🟢 Inactif'}\n"
                    f"[📊 Activité] {activity}```"
                ),
                inline=True
            )

        embed.set_footer(
            text=f"Dernière actualisation: {datetime.now().strftime('%H:%M:%S')}",
            icon_url="https://github.com/Momonga-OP/Start2000/blob/main/hourglass.png?raw=true"
        )

        return embed

    async def ensure_panel(self):
        """
        Ensure the alert panel message exists and is up-to-date.
        """
        await self.update_member_counts()

        guild = self.bot.get_guild(GUILD_ID)
        if not guild:
            return

        channel = guild.get_channel(PING_DEF_CHANNEL_ID)
        if not channel:
            return

        if not self.panel_message:
            async for msg in channel.history(limit=20):
                if msg.author == self.bot.user and msg.pinned:
                    self.panel_message = msg
                    break

        view = GuildPingView(self.bot)
        embed = await self.create_panel_embed()

        if self.panel_message:
            try:
                await self.panel_message.edit(embed=embed, view=view)
            except discord.NotFound:
                self.panel_message = None
                await self.ensure_panel()
        else:
            self.panel_message = await channel.send(embed=embed, view=view)
            await self.panel_message.pin(reason="Mise à jour du panneau")

    async def handle_ping(self, guild_name: str) -> bool | float:
        """
        Handle cooldown logic for guild pings.
        Returns True if the ping is allowed, or the remaining cooldown time in seconds otherwise.
        """
        now = datetime.now().timestamp()
        if guild_name in self.cooldowns and now < self.cooldowns[guild_name]:
            return self.cooldowns[guild_name] - now

        self.cooldowns[guild_name] = now + 15  # Set cooldown to 15 seconds
        return True

    @commands.command(name="alerte_guild")
    async def ping_guild(self, ctx, guild_name: str):
        """
        Trigger an alert for the specified guild.
        """
        cooldown = await self.handle_ping(guild_name)
        if isinstance(cooldown, float):
            embed = discord.Embed(
                title="⏳ Temporisation Active",
                description=f"Veuillez patienter {cooldown:.1f}s avant une nouvelle alerte pour {guild_name}",
                color=discord.Color.orange()
            )
            return await ctx.send(embed=embed)

        self.add_ping_record(guild_name, ctx.author.id)
        await self.ensure_panel()

        stats = self.get_ping_stats(guild_name)
        response = discord.Embed(
            title=f"🚨 Alerte {guild_name} Activée",
            description=f"🔔 {self.member_counts.get(guild_name, 0)} membres disponibles",
            color=discord.Color.green()
        )
        response.add_field(
            name="Détails",
            value=f"**Initiateur:** {ctx.author.mention}\n"
                  f"**Canal:** {ctx.channel.mention}\n"
                  f"**Priorité:** `Urgente`",
            inline=False
        )
        response.add_field(
            name="Statistiques",
            value=f"```diff\n+ Pings 24h: {stats['total_24h']}\n"
                  f"+ Uniques: {stats['unique_24h']}\n"
                  f"- Prochaine alerte possible dans: 15s```",
            inline=False
        )

        await ctx.send(embed=response)
        await self.send_alert_log(guild_name, ctx.author)

    async def send_alert_log(self, guild_name: str, author: discord.Member):
        """
        Log the alert to the designated channel.
        """
        guild = self.bot.get_guild(GUILD_ID)
        if not guild:
            return

        channel = guild.get_channel(ALERTE_DEF_CHANNEL_ID)
        if not channel:
            return

        log_embed = discord.Embed(
            title=f"🚩 Alerte {guild_name}",
            description=f"@here · Défenseurs requis · {self.member_counts.get(guild_name, 0)} disponibles",
            color=discord.Color.red()
        )
        log_embed.add_field(
            name="Informations",
            value=f"**Initiateur:** {author.mention}\n"
                  f"**Heure:** {discord.utils.format_dt(datetime.now(), 'F')}\n"
                  f"**Statut serveur:** `Stable`",
            inline=False
        )
        log_embed.add_field(
            name="Actions Requises",
            value="```fix\n1. Confirmer disponibilité\n2. Rejoindre le canal vocal\n3. Suivre les instructions```",
            inline=False
        )

        await channel.send(embed=log_embed)

    @commands.Cog.listener()
    async def on_ready(self):
        """
        Perform setup tasks when the bot is ready.
        """
        await self.ensure_panel()

        guild = self.bot.get_guild(GUILD_ID)
        if guild:
            alert_channel = guild.get_channel(ALERTE_DEF_CHANNEL_ID)
            if alert_channel:
                await alert_channel.set_permissions(
                    guild.default_role,
                    send_messages=False,
                    add_reactions=False,
                    create_public_threads=False
                )

        await self.bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"{sum(self.member_counts.values())} défenseurs"
            )
        )
        print(f"✅ Système opérationnel • {datetime.now().strftime('%d/%m/%Y %H:%M')}")

async def setup(bot: commands.Bot):
    """
    Add the StartGuildCog to the bot.
    """
    await bot.add_cog(StartGuildCog(bot))
