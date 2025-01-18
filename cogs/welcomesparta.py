import discord
from discord.ext import commands

class WelcomeSparta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Ensure the bot detects new members when they join the specific server
        if member.guild.id == 1300093554064097400:  # Target server ID
            try:
                # Log the detection of a new member
                print(f"Detected new member: {member.name} joined the server {member.guild.name}.")

                # Announce welcome message in the specified channel
                public_channel = member.guild.get_channel(1300093554399645707)  # Public channel ID
                if public_channel:
                    welcome_message = (
                        f"🎉 Bienvenue {member.mention} à Sparta! 🎉\n"
                        "Nous sommes ravis de vous accueillir ici ! N'oubliez pas de consulter nos salons et de profiter de votre séjour. 🎊"
                    )
                    image_url = "https://github.com/Momonga-OP/Start2000/blob/main/Alliance%20Start2000.png?raw=true"
                    embed = discord.Embed(description=welcome_message, color=discord.Color.blue())
                    embed.set_image(url=image_url)
                    await public_channel.send(embed=embed)
                    print(f"Welcome message sent successfully for {member.name}.")
                else:
                    print("Public channel not found or inaccessible.")

            except Exception as e:
                print(f"Error in on_member_join: {e}")

    @commands.Cog.listener()
    async def on_ready(self):
        # Ensure the bot is ready and connected to the target channel
        guild = self.bot.get_guild(1300093554064097400)
        if guild:
            public_channel = guild.get_channel(1300093554399645707)
            if public_channel:
                print(f"Bot is now focused on channel: {public_channel.name} (ID: {public_channel.id}) in server {guild.name}.")
            else:
                print("Target public channel not found or inaccessible.")
        else:
            print("Target guild not found or inaccessible.")

async def setup(bot):
    await bot.add_cog(WelcomeSparta(bot))
    print("WelcomeSparta cog loaded successfully.")
