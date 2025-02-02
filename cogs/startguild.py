import discord
from discord.ext import commands
from collections import defaultdict
from datetime import datetime, timedelta
import asyncio
from typing import Dict, List, Optional
from .config import GUILD_ID, PING_DEF_CHANNEL_ID, ALERTE_DEF_CHANNEL_ID
from .views import GuildPingView

class CooldownManager:
    def __init__(self, cooldown_time: int = 30):
        self.cooldowns: Dict[str, Dict[int, datetime]] = defaultdict(dict)
        self.cooldown_time = cooldown_time

    def is_on_cooldown(self, guild_name: str, user_id: int) -> tuple[bool, Optional[int]]:
        """
        Check if a user is on cooldown for a specific guild.
        Returns (is_on_cooldown, seconds_remaining)
        """
        if guild_name not in self.cooldowns or user_id not in self.cooldowns[guild_name]:
            return False, None

        last_used = self.cooldowns[guild_name][user_id]
        now = datetime.now()
        time_passed = (now - last_used).total_seconds()
        
        if time_passed < self.cooldown_time:
            return True, int(self.cooldown_time - time_passed)
        return False, None

    def add_cooldown(self, guild_name: str, user_id: int):
        """Add a cooldown for a user in a specific guild."""
        self.cooldowns[guild_name][user_id] = datetime.now()

    def cleanup_old_cooldowns(self):
        """Remove expired cooldowns to prevent memory leaks."""
        now = datetime.now()
        threshold = now - timedelta(seconds=self.cooldown_time)
        
        for guild_name in list(self.cooldowns.keys()):
            self.cooldowns[guild_name] = {
                user_id: timestamp
                for user_id, timestamp in self.cooldowns[guild_name].items()
                if timestamp > threshold
            }

class StartGuildCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.cooldown_manager = CooldownManager(30)  # 30 second cooldown
        self.ping_history = defaultdict(list)
        self.member_counts = {}
        self.cleanup_task = None

    async def cog_load(self):
        """Called when the cog is loaded."""
        self.cleanup_task = self.bot.loop.create_task(self.periodic_cleanup())

    async def cog_unload(self):
        """Called when the cog is unloaded."""
        if self.cleanup_task:
            self.cleanup_task.cancel()

    async def periodic_cleanup(self):
        """Periodically clean up old cooldowns and ping history."""
        while True:
            try:
                self.cooldown_manager.cleanup_old_cooldowns()
                # Keep only last 24 hours of ping history
                now = datetime.now()
                day_ago = now - timedelta(days=1)
                for guild_name in self.ping_history:
                    self.ping_history[guild_name] = [
                        ping for ping in self.ping_history[guild_name]
                        if ping['timestamp'] > day_ago
                    ]
                await asyncio.sleep(300)  # Run cleanup every 5 minutes
            except Exception as e:
                print(f"Error in cleanup task: {e}")
                await asyncio.sleep(60)  # Wait a minute before retrying

    async def update_member_counts(self):
        """Update active member counts for each guild role."""
        try:
            guild = self.bot.get_guild(GUILD_ID)
            if not guild:
                raise ValueError("Guild not found")
            
            self.member_counts.clear()
            for role in guild.roles:
                if role.name.startswith("DEF"):
                    self.member_counts[role.name] = len(role.members)
        except Exception as e:
            print(f"Error updating member counts: {e}")

    def add_ping_record(self, guild_name: str, author_id: int):
        """Record a ping event with error handling."""
        try:
            timestamp = datetime.now()
            self.ping_history[guild_name].append({
                'author_id': author_id,
                'timestamp': timestamp
            })
            # Keep only the last 100 pings
            self.ping_history[guild_name] = self.ping_history[guild_name][-100:]
        except Exception as e:
            print(f"Error recording ping: {e}")

    def get_ping_stats(self, guild_name: str) -> dict:
        """Calculate ping statistics with error handling."""
        try:
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
        except Exception as e:
            print(f"Error getting ping stats: {e}")
            return {'total_24h': 0, 'unique_users_24h': 0, 'member_count': 0}

    async def ensure_panel(self):
        """Ensures that the panel for the alert system is updated or created."""
        try:
            await self.update_member_counts()

            guild = self.bot.get_guild(GUILD_ID)
            if not guild:
                raise ValueError("Guild not found")

            channel = guild.get_channel(PING_DEF_CHANNEL_ID)
            if not channel:
                raise ValueError("Ping definition channel not found")

            view = GuildPingView(self.bot)
            embed = await self._create_panel_embed()

            # Find and update existing pinned message
            async for message in channel.history(limit=50):
                if message.pinned:
                    await message.edit(embed=embed, view=view)
                    return

            # Create new message if none found
            new_message = await channel.send(embed=embed, view=view)
            await new_message.pin()
            
        except Exception as e:
            print(f"Error ensuring panel: {e}")

    async def _create_panel_embed(self) -> discord.Embed:
        """Create the panel embed with error handling."""
        try:
            embed = discord.Embed(
                title="🎯 Panneau d'Alerte DEF",
                description=(
                    "Bienvenue sur le **Panneau d'Alerte Défense** !\n\n"
                    "Utilisez les boutons ci-dessous pour envoyer une alerte à votre guilde. "
                    "Un délai de 30 secondes est appliqué entre chaque utilisation par personne.\n\n"
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

            return embed
        except Exception as e:
            print(f"Error creating panel embed: {e}")
            return discord.Embed(title="Error", description="An error occurred while creating the panel.")

    @commands.command(name="ping_guild")
    async def ping_guild(self, ctx, guild_name: str):
        """Command to ping a guild with statistics and cooldown."""
        try:
            # Check if user is on cooldown
            is_cooldown, remaining = self.cooldown_manager.is_on_cooldown(guild_name, ctx.author.id)
            if is_cooldown:
                await ctx.send(
                    f"⏳ Veuillez attendre encore {remaining} secondes avant de ping à nouveau la guilde {guild_name}."
                )
                return

            guild = self.bot.get_guild(GUILD_ID)
            if not guild:
                await ctx.send("⚠️ Guild not found. Check the GUILD_ID in your configuration.")
                return

            # Add cooldown and record ping
            self.cooldown_manager.add_cooldown(guild_name, ctx.author.id)
            self.add_ping_record(guild_name, ctx.author.id)
            
            # Update panel and send confirmation
            await self.ensure_panel()
            stats = self.get_ping_stats(guild_name)
            
            await ctx.send(
                f"✅ La guilde {guild_name} a été pingée !\n"
                f"📊 C'est le {stats['total_24h']}e ping aujourd'hui."
            )

        except Exception as e:
            await ctx.send(f"❌ Une erreur s'est produite: {str(e)}")
            print(f"Error in ping_guild command: {e}")

async def setup(bot: commands.Bot):
    """Setup function to add the StartGuildCog to the bot."""
    await bot.add_cog(StartGuildCog(bot))
