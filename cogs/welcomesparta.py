import discord
from discord.ext import commands
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WelcomeSparta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.guild.id == 1300093554064097400:
            logger.info(f"Detected new member: {member.name} joined the server {member.guild.name}.")
            
            public_channel = member.guild.get_channel(1300093554399645707)
            if not public_channel:
                logger.error(f"Could not find public channel with ID: {1300093554399645707}")
                return
                
            try:
                welcome_message = (
                    f"🎉 Bienvenue {member.mention} à Sparta! 🎉\n"
                    "Nous sommes ravis de vous accueillir ici ! N'oubliez pas de consulter nos salons et de profiter de votre séjour. 🎊"
                )
                image_url = "https://github.com/Momonga-OP/Start2000/blob/main/Alliance%20Start2000.png?raw=true"
                embed = discord.Embed(description=welcome_message, color=discord.Color.blue())
                embed.set_image(url=image_url)
                
                await public_channel.send(embed=embed)
                logger.info(f"Welcome message sent successfully for {member.name}.")
                
            except discord.Forbidden:
                logger.error("Bot doesn't have permission to send messages in the channel")
            except discord.HTTPException as e:
                logger.error(f"Failed to send welcome message: {e}")
            except Exception as e:
                logger.error(f"Unexpected error in on_member_join: {e}")

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f'Welcome cog ready!')
        guild = self.bot.get_guild(1300093554064097400)
        if not guild:
            logger.error("Could not find the specified guild")
            return
            
        public_channel = guild.get_channel(1300093554399645707)
        if public_channel:
            logger.info(f"Bot is ready in channel: {public_channel.name} (ID: {public_channel.id}) in server {guild.name}")
        else:
            logger.error("Target public channel not found")

    # Test command to verify bot permissions
    @commands.command()
    async def test(self, ctx):
        """Test command to verify bot is working"""
        try:
            test_embed = discord.Embed(
                description="Test message - Bot is working!",
                color=discord.Color.green()
            )
            await ctx.send(embed=test_embed)
            logger.info("Test command executed successfully")
        except Exception as e:
            logger.error(f"Error in test command: {e}")

async def setup(bot):
    await bot.add_cog(WelcomeSparta(bot))
    logger.info("WelcomeSparta cog loaded successfully.")
