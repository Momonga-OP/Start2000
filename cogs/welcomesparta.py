import discord
from discord.ext import commands

class WelcomeSparta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Check if the member joined the specific server
        if member.guild.id == 1300093554064097400:  # Target server ID
            try:
                # Send public welcome message
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
                    print(f"Public welcome message sent successfully for {member.name}.")
                else:
                    print("Public channel not found or inaccessible.")

                # Log member join
                print(f"New member detected: {member.name} joined {member.guild.name}.")
            except Exception as e:
                print(f"Error in on_member_join: {e}")

async def setup(bot):
    await bot.add_cog(WelcomeSparta(bot))
    print("WelcomeSparta cog loaded successfully.")
