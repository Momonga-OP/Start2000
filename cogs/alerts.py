import discord
from discord.ext import commands
from discord import app_commands
from discord.utils import utcnow
from datetime import timedelta
import os
import re
import logging
import aiofiles
from discord.ext.commands import CooldownMapping

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Alerts(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.allowed_channel_id = 1247728738326679583  # Replace with your specific channel ID
        self._cd = CooldownMapping.from_cooldown(1, 60, commands.BucketType.user)  # 1 use per 60 seconds per user

    def filter_relevant_messages(self, messages):
        """Filter messages that are sent by bots and mention everyone or roles."""
        return [
            message for message in messages
            if message.author.bot and (message.mention_everyone or message.role_mentions)
        ]

    def parse_notification_data(self, message):
        """Parse notification data from a message."""
        attacker_match = re.search(r"Attacker:\s*(\w+)", message.content, re.IGNORECASE)
        outcome_match = re.search(r"Outcome:\s*(Win|Loss)", message.content, re.IGNORECASE)
        return {
            "timestamp": message.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "roles_tagged": [role.name for role in message.role_mentions],
            "attacker": attacker_match.group(1) if attacker_match else "Unknown",
            "outcome": outcome_match.group(1) if outcome_match else "Not Specified"
        }

    async def generate_report(self, notification_data, now):
        """Generate a report file with notification data."""
        report_filename = f"notification_report_{now.strftime('%Y%m%d_%H%M%S')}.txt"
        async with aiofiles.open(report_filename, "w") as report_file:
            if not notification_data:
                await report_file.write("No notifications were sent in the last 7 days.\n")
            else:
                for user_id, data in notification_data.items():
                    await report_file.write(f"User: {data['username']}\n")
                    await report_file.write(f"Total Notifications Sent: {len(data['notifications'])}\n\n")
                    for notification in data["notifications"]:
                        await report_file.write(f"  - Timestamp: {notification['timestamp']}\n")
                        await report_file.write(f"    Roles Tagged: {', '.join(notification['roles_tagged']) if notification['roles_tagged'] else 'None'}\n")
                        await report_file.write(f"    Attacker: {notification['attacker']}\n")
                        await report_file.write(f"    Outcome: {notification['outcome']}\n\n")
        return report_filename

    @app_commands.command(name="alert", description="Generate a report of notifications sent in this channel for the last 7 days.")
    async def alert(self, interaction: discord.Interaction):
        """Generate a report of notifications sent in the last 7 days."""
        # Check cooldown
        bucket = self._cd.get_bucket(interaction.user)  # Use interaction.user instead of interaction.message
        retry_after = bucket.update_rate_limit()
        if retry_after:
            await interaction.response.send_message(f"Please wait {retry_after:.2f} seconds before using this command again.", ephemeral=True)
            return

        # Ensure the command is only used in the specified channel
        if interaction.channel_id != self.allowed_channel_id:
            await interaction.response.send_message("This command can only be used in the designated channel.", ephemeral=True)
            return

        # Get the message history for the last 7 days
        channel = interaction.channel
        now = utcnow()
        seven_days_ago = now - timedelta(days=7)

        try:
            # Collect relevant messages asynchronously
            messages = []
            async for message in channel.history(after=seven_days_ago):
                messages.append(message)

            # Filter relevant messages
            relevant_messages = self.filter_relevant_messages(messages)

            # Collect notification data
            notification_data = {}
            for message in relevant_messages:
                author = message.author
                parsed_data = self.parse_notification_data(message)

                # Initialize data for the author if not already done
                if author.id not in notification_data:
                    notification_data[author.id] = {
                        "username": author.name,
                        "notifications": []
                    }

                # Append notification details
                notification_data[author.id]["notifications"].append(parsed_data)

            # Generate the report
            report_filename = await self.generate_report(notification_data, now)

            # Notify the user and attach the file
            await interaction.response.send_message("Report generated:", file=discord.File(report_filename), ephemeral=True)

            # Clean up the file after sending
            os.remove(report_filename)

        except discord.Forbidden:
            await interaction.response.send_message("I don't have permission to read messages in this channel.", ephemeral=True)
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Alerts(bot))
