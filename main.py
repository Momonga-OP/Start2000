import discord
from discord.ext import commands
import os
import asyncio
import logging
from database import initialize_db  # Import the database initialization function

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Create the bot
bot = commands.Bot(command_prefix='!', intents=intents)

# Constants
OWNER_ID = 486652069831376943  # Replace with your Discord user ID
TOKEN = os.getenv('DISCORD_TOKEN')

# Initialize the database
initialize_db()

@bot.event
async def on_ready():
    """Event triggered when the bot is ready."""
    logger.info(f'Logged in as {bot.user}')
    await sync_commands()

async def sync_commands():
    """Sync slash commands with Discord."""
    if not hasattr(bot, 'synced'):
        try:
            synced = await bot.tree.sync()
            logger.info(f"Synced {len(synced)} commands")
            bot.synced = True
        except Exception as e:
            logger.exception("Failed to sync commands")

@bot.command(name='memory')
async def memory_command(ctx):
    """Command to notify users about memory management."""
    await ctx.send("Memory management has been removed from this bot.")

@bot.event
async def on_message(message: discord.Message):
    """Event triggered when a message is sent."""
    if message.author != bot.user:
        logger.info(f"Message from {message.author}: {message.content}")

    # Forward DMs to the bot owner
    if isinstance(message.channel, discord.DMChannel) and message.author != bot.user:
        await forward_dm(message)

    # Process commands
    await bot.process_commands(message)

async def forward_dm(message: discord.Message):
    """Forward DMs to the bot owner."""
    owner = await bot.fetch_user(OWNER_ID)
    if owner:
        await owner.send(f"Message from {message.author}: {message.content}")

@bot.event
async def on_disconnect():
    """Event triggered when the bot disconnects."""
    logger.info("Bot disconnected")

@bot.event
async def on_error(event: str, *args, **kwargs):
    """Event triggered when an error occurs."""
    logger.exception(f"An error occurred in event {event}")

@bot.event
async def on_close():
    """Event triggered when the bot is closing."""
    logger.info("Bot is closing")
    await close_sessions()

async def close_sessions():
    """Perform cleanup before closing the bot."""
    logger.info("Performing cleanup before closing...")

# List of extensions (cogs) to load
EXTENSIONS = [
    'cogs.admin',
    'cogs.relocate', 'cogs.watermark', 'cogs.talk', 'cogs.role', 'cogs.tencent',
    'cogs.watermark_user', 'cogs.metiers',
    'cogs.image_converter', 'cogs.startguild', 'cogs.clear',
    'cogs.alerts', 'cogs.welcomesparta',
    'cogs.super', 'cogs.translator', 'cogs.voice', 'cogs.rules', 'cogs.write', 'cogs.dofustouch',
]

async def load_extensions():
    """Load all extensions (cogs) listed in EXTENSIONS."""
    for extension in EXTENSIONS:
        try:
            await bot.load_extension(extension)
            logger.info(f"Loaded extension: {extension}")
        except Exception as e:
            logger.exception(f"Failed to load extension {extension}")

async def main():
    """Main function to start the bot."""
    async with bot:
        # Load extensions
        await load_extensions()

        # Check if the bot token is available
        if not TOKEN:
            logger.error("Bot token not found")
            return

        # Start the bot
        try:
            await bot.start(TOKEN)
        except discord.LoginFailure:
            logger.error("Invalid token")
        except Exception as e:
            logger.exception("Failed to start the bot")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.exception("Bot encountered an error and stopped")
