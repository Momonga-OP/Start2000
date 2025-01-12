import discord
from discord.ext import commands

class WelcomeSparta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Server and channel configuration
        server_channels = {
            1300093554064097400: 1300093554399645707,  # Sparta server and its public channel
            1217700740949348443: 1247706162317758597,  # Second server and its public channel
        }

        # Check if the member joined one of the specified servers
        if member.guild.id in server_channels:
            public_channel_id = server_channels[member.guild.id]
            public_channel = member.guild.get_channel(public_channel_id)

            if public_channel:
                try:
                    # Send public welcome message
                    welcome_message = (
                        f"🎉 Welcome {member.mention} to {member.guild.name}! 🎉\n"
                        "We're thrilled to have you here! Make sure to check out our channels and enjoy your stay. 🎊"
                    )
                    image_url = "https://github.com/Momonga-Og/Spectra/blob/db4e92dd8deaba15608bd0856f265f742097fc72/th.jpeg?raw=true"
                    embed = discord.Embed(description=welcome_message, color=discord.Color.blue())
                    embed.set_image(url=image_url)
                    await public_channel.send(embed=embed)
                    print(f"Public welcome message sent successfully to {member.name} in server {member.guild.name}.")
                except Exception as e:
                    print(f"Error sending welcome message in server {member.guild.name}: {e}")
            else:
                print(f"Public channel with ID {public_channel_id} not found or inaccessible in server {member.guild.name}.")
        else:
            print(f"Member joined an untracked server: {member.guild.name} (ID: {member.guild.id}).")

async def setup(bot):
    await bot.add_cog(WelcomeSparta(bot))
    print("WelcomeSparta cog loaded successfully.")
