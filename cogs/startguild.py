import discord
from discord.ext import commands
from collections import defaultdict
from datetime import datetime, timedelta
import asyncio
from typing import Optional
from .config import GUILD_ID, PING_DEF_CHANNEL_ID, ALERTE_DEF_CHANNEL_ID
from .views import GuildPingView  # Assuming you have this view setup

class StartGuildCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.cooldowns = {}
        self.ping_history = defaultdict(list)
        self.member_counts = {}
        self.panel_message: Optional[discord.Message] = None

    # Helper function for creating progress bars
    @staticmethod
    def create_progress_bar(percentage: float, length: int = 10) -> str:
        filled = '▰' * int(round(percentage * length))
        empty = '▱' * (length - len(filled))
        return f"{filled}{empty} {int(percentage * 100)}%"

    async def update_member_counts(self):
        """Update active member counts with status check"""
        guild = self.bot.get_guild(GUILD_ID)
        if guild:
            for role in guild.roles:
                if role.name.startswith("DEF"):
                    # Count only members with online status
                    self.member_counts[role.name] = sum(
                        1 for m in role.members 
                        if not m.bot and m.status == discord.Status.online
                    )

    def add_ping_record(self, guild_name: str, author_id: int):
        """Record a ping event with cleanup"""
        timestamp = datetime.now()
        self.ping_history[guild_name].append({
            'author_id': author_id,
            'timestamp': timestamp
        })
        # Keep history for 7 days but only last 100 entries
        self.ping_history[guild_name] = [
            ping for ping in self.ping_history[guild_name] 
            if ping['timestamp'] > datetime.now() - timedelta(days=7)
        ][-100:]

    def get_ping_stats(self, guild_name: str) -> dict:
        """Enhanced stats with weekly trends"""
        now = datetime.now()
        time_ranges = {
            '24h': now - timedelta(hours=24),
            '7d': now - timedelta(days=7)
        }

        stats = {'member_count': self.member_counts.get(guild_name, 0)}
        
        for period, cutoff in time_ranges.items():
            pings = [p for p in self.ping_history[guild_name] if p['timestamp'] > cutoff]
            stats.update({
                f'total_{period}': len(pings),
                f'unique_{period}': len({p['author_id'] for p in pings}),
                f'active_{period}': min(100, len(pings) * 2)  # Example metric
            })
        
        return stats

    async def create_panel_embed(self) -> discord.Embed:
        """Create a richly formatted embed for the panel"""
        embed = discord.Embed(
            title="🛡️ Alliance DEF Alert System",
            color=discord.Color.gold(),
            timestamp=datetime.now()
        )
        
        # Header Section
        embed.set_author(
            name="START Alliance Defense Command",
            icon_url="https://cdn.discordapp.com/attachments/929850884006211594/1127117558352080926/shield.png"
        )
        
        embed.set_thumbnail(
            url="https://cdn.discordapp.com/attachments/929850884006211594/1127117558352080926/shield.png"
        )

        # Main Description
        embed.description = (
            "```diff\n+ ACTIVE DEFENSE MONITORING SYSTEM [v2.4.1]\n```\n"
            "📌 **Core Functionality:**\n"
            "◈ Real-time guild alert coordination\n"
            "◈ Automated cooldown management\n"
            "◈ Detailed engagement analytics\n\n"
            "🕹️ **Control Interface:**\n"
            "Use the button matrix below to activate guild alerts\n"
            "```ansi\n[2;34m[!] Cooldown Status: [0m[2;32mACTIVE[0m\n"
            "[2;34m[!] System Health: [0m[2;32mOPTIMAL[0m```"
        )

        # Statistics Fields
        for guild_name, count in self.member_counts.items():
            stats = self.get_ping_stats(guild_name)
            activity = self.create_progress_bar(stats['active_24h'] / 100)
            
            field_value = (
                f"```prolog\n"
                f"[Members]  {count}/50 {'⭐' if count >= 45 else '🔹'}\n"
                f"[24h]     {stats['total_24h']} pings ({stats['unique_24h']} users)\n"
                f"[7d]      {stats['total_7d']} pings ({stats['unique_7d']} users)\n"
                f"Activity: {activity}```"
            )
            
            embed.add_field(
                name=f"📊 {guild_name} Statistics",
                value=field_value,
                inline=True
            )

        # Status Footer
        embed.set_footer(
            text="Defense Coordination System • Real-time Monitoring",
            icon_url="https://cdn.discordapp.com/embed/avatars/4.png"
        )
        
        return embed

    async def ensure_panel(self):
        """Enhanced panel management with message caching"""
        await self.update_member_counts()

        guild = self.bot.get_guild(GUILD_ID)
        if not guild:
            return

        channel = guild.get_channel(PING_DEF_CHANNEL_ID)
        if not channel:
            return

        # Check existing panel message
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
            await self.panel_message.pin(reason="Initial panel pin")

    async def handle_ping(self, guild_name):
        """Cooldown handler with visual feedback"""
        if self.cooldowns.get(guild_name):
            remaining = self.cooldowns[guild_name] - datetime.now()
            return remaining.total_seconds()

        self.cooldowns[guild_name] = datetime.now() + timedelta(seconds=15)
        return True

    @commands.command(name="ping_guild")
    async def ping_guild(self, ctx, guild_name: str):
        """Enhanced ping command with rich response"""
        cooldown_status = await self.handle_ping(guild_name)
        if isinstance(cooldown_status, float):
            embed = discord.Embed(
                title="⏳ Cooldown Active",
                description=f"**{guild_name}** alerts can be triggered again in {cooldown_status:.1f}s",
                color=discord.Color.orange()
            )
            embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1127120140033732678.gif")
            return await ctx.send(embed=embed)

        self.add_ping_record(guild_name, ctx.author.id)
        await self.ensure_panel()

        # Create response embed
        stats = self.get_ping_stats(guild_name)
        response = discord.Embed(
            title=f"🚨 {guild_name} Alert Activated",
            color=discord.Color.green()
        )
        response.add_field(
            name="Activation Details",
            value=f"**Initiator:** {ctx.author.mention}\n"
                  f"**Location:** {ctx.channel.mention}\n"
                  f"**Priority:** `HIGH`",
            inline=False
        )
        response.add_field(
            name="Recent Activity",
            value=f"```diff\n+ 24h Pings: {stats['total_24h']} ({stats['unique_24h']} users)\n"
                  f"+ 7d Total: {stats['total_7d']} pings\n"
                  f"- Cooldown: 15s remaining```",
            inline=False
        )
        response.set_footer(text="Defense Coordination System • Alert Acknowledged")
        
        await ctx.send(embed=response)
        await self.send_alert_log(guild_name, ctx.author)

    async def send_alert_log(self, guild_name: str, author: discord.Member):
        """Send formatted alert to the alert channel"""
        guild = self.bot.get_guild(GUILD_ID)
        channel = guild.get_channel(ALERTE_DEF_CHANNEL_ID)
        
        if not channel:
            return

        log_embed = discord.Embed(
            title=f"📢 {guild_name} Defense Alert",
            description=f"**Alert initiated by:** {author.mention}\n"
                        f"**Timestamp:** {discord.utils.format_dt(datetime.now(), 'F')}",
            color=discord.Color.blurple()
        )
        log_embed.add_field(
            name="Response Protocol",
            value="```fix\n[REQUIRED ACTIONS]\n1. Confirm alert in command channel\n"
                  "2. Deploy reconnaissance\n3. Establish defense perimeter```",
            inline=False
        )
        log_embed.set_author(
            name="START Alliance Defense Command",
            icon_url=guild.icon.url if guild.icon else None
        )
        
        await channel.send(f"@here {guild_name} Defense Alert", embed=log_embed)

    @commands.Cog.listener()
    async def on_ready(self):
        """Enhanced ready handler with status updates"""
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
                
        # Update presence with custom status
        await self.bot.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="Defense Alerts"
            )
        )
        print(f"🛡️ Defense System Online in {len(self.bot.guilds)} guilds")

async def setup(bot: commands.Bot):
    await bot.add_cog(StartGuildCog(bot))
