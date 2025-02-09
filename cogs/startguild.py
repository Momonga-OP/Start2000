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
        self.bot = bot
        self.cooldowns = {}
        self.ping_history = defaultdict(list)
        self.member_counts = {}
        self.panel_message: Optional[discord.Message] = None

    @staticmethod
    def create_progress_bar(percentage: float, length: int = 10) -> str:
        filled = '▰' * int(round(percentage * length))
        empty = '▱' * (length - len(filled))
        return f"{filled}{empty} {int(percentage * 100)}%"

    async def update_member_counts(self):
        """Mise à jour précise des membres connectés"""
        guild = self.bot.get_guild(GUILD_ID)
        if guild:
            await guild.chunk()
            for role in guild.roles:
                if role.name.startswith("DEF"):
                    self.member_counts[role.name] = sum(
                        1 for m in role.members 
                        if not m.bot and m.status in (discord.Status.online, discord.Status.idle, discord.Status.dnd)
                    )

    def add_ping_record(self, guild_name: str, author_id: int):
        timestamp = datetime.now()
        self.ping_history[guild_name].append({'author_id': author_id, 'timestamp': timestamp})
        self.ping_history[guild_name] = [
            ping for ping in self.ping_history[guild_name] if ping['timestamp'] > datetime.now() - timedelta(days=7)
        ][-100:]

    def get_ping_stats(self, guild_name: str) -> dict:
        now = datetime.now()
        periodes = {'24h': now - timedelta(hours=24), '7j': now - timedelta(days=7)}
        stats = {'member_count': self.member_counts.get(guild_name, 0)}
        
        for periode, cutoff in periodes.items():
            pings = [p for p in self.ping_history[guild_name] if p['timestamp'] > cutoff]
            stats.update({
                f'total_{periode}': len(pings),
                f'unique_{periode}': len({p['author_id'] for p in pings}),
                f'activite_{periode}': min(100, len(pings) * 2)
            })
        
        return stats

    async def create_panel_embed(self) -> discord.Embed:
        await self.update_member_counts()
        embed = discord.Embed(
            title="🛡️ Panneau d'Alerte Défense",
            color=discord.Color.gold(),
            timestamp=datetime.now()
        )
        total_connectes = sum(self.member_counts.values())
        embed.description = (
            "```diff\n+ SYSTÈME D'ALERTE GUILDE [v2.7.0]\n```\n"
            "👥 Membres connectés: {}\n"
            "```ansi\n[2;34m[!] Statut système: [0m[2;32mOPÉRATIONNEL[0m```".format(total_connectes)
        )
        
        for guild_name, count in self.member_counts.items():
            stats = self.get_ping_stats(guild_name)
            activite = self.create_progress_bar(stats['activite_24h'] / 100)
            valeur = (
                f"```prolog\n[🟢 Connectés] {count}\n"
                f"[📨 Pings 24h] {stats['total_24h']}\n"
                f"[⏱ Cooldown] {'🟠 Actif' if self.cooldowns.get(guild_name) else '🟢 Inactif'}\n"
                f"[📊 Activité] {activite}```"
            )
            embed.add_field(name=f"📌 {guild_name}", value=valeur, inline=True)
        
        return embed

    async def ensure_panel(self):
        await self.update_member_counts()
        guild = self.bot.get_guild(GUILD_ID)
        if not guild:
            return
        channel = guild.get_channel(PING_DEF_CHANNEL_ID)
        if not channel:
            return
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
            await self.panel_message.pin()

    @commands.Cog.listener()
    async def on_ready(self):
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
    await bot.add_cog(StartGuildCog(bot))
