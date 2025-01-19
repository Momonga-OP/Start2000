import discord
from discord.ext import commands
import aiohttp

class Rules(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.rules_url = "https://github.com/Momonga-OP/Start2000/blob/b64b2bf3cc6d9e6f44d92b8e69c446ca8427df25/rules.txt"
        self.rules_channel_id = 1300093554399645708  # Channel ID where rules are posted
        self.role_to_assign = 1330547847720079450  # Role ID to assign when users agree

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.bot.user} is ready and Rules Cog is active!")
        # Post the rules when the bot starts
        await self.post_rules()

    async def fetch_rules(self):
        """Fetch rules content from the provided URL."""
        async with aiohttp.ClientSession() as session:
            async with session.get(self.rules_url) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    print("Failed to fetch rules content.")
                    return None

    async def post_rules(self):
        channel = self.bot.get_channel(self.rules_channel_id)
        if not channel:
            print("Rules channel not found. Please check the ID.")
            return

        rules_content = await self.fetch_rules()
        if rules_content:
            embed = discord.Embed(
                title="Server Rules",
                description=rules_content,
                color=discord.Color.blue()
            )
            embed.set_footer(text="Please react to agree and gain access to the server.")

            # Delete old messages and post new rules
            await channel.purge(limit=10)
            rules_message = await channel.send(embed=embed)
            await rules_message.add_reaction("✅")  # Checkmark emoji

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.channel_id == self.rules_channel_id and str(payload.emoji) == "✅":
            guild = self.bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            role = guild.get_role(self.role_to_assign)
            if member and role:
                await member.add_roles(role)
                print(f"Assigned role {role.name} to {member.display_name}.")

async def setup(bot):
    await bot.add_cog(Rules(bot))
