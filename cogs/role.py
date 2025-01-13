import discord
from discord.ext import commands

# Role data
ROLE_DATA = {
    "Darkness": {
        "emoji": "<:Darkness:1307418763276324944>",
        "role_id": 1300093554064097407,
        "role_name": "Darkness",
    },
    "GTO": {
        "emoji": "<:GTO:1307418692992237668>",
        "role_id": 1300093554080612363,
        "role_name": "GTO",
    },
    "Aversion": {
        "emoji": "<:aversion:1307418759002198086>",
        "role_id": 1300093554064097409,
        "role_name": "Aversion",
    },
    "LMDF": {
        "emoji": "<:lmdf:1307418765142786179>",
        "role_id": 1300093554080612364,
        "role_name": "LMDF",
    },
    "Notorious": {
        "emoji": "<:notorious:1307418766266728500>",
        "role_id": 1300093554064097406,
        "role_name": "Notorious",
    },
    "Percophile": {
        "emoji": "<:percophile:1307418769764651228>",
        "role_id": 1300093554080612362,
        "role_name": "Percophile",
    },
    "Tilisquad": {
        "emoji": "<:tilisquad:1307418771882905600>",
        "role_id": 1300093554080612367,
        "role_name": "Tilisquad",
    },
    "Crescent": {
        "emoji": "<:Crescent:1328374098262495232>",
        "role_id": 1300093554064097404,
        "role_name": "Crescent",
    },
    "DieHard": {
        "emoji": "<:DieHard:1328374141237329972>",
        "role_id": 1300093554064097405,
        "role_name": "DieHard",
    },
    "Deviance": {
        "emoji": "<:Deviance:1328387647386947664>",
        "role_id": 1300093554064097408,
        "role_name": "Deviance",
    },
}

class RoleSelectionView(discord.ui.View):
    def __init__(self, bot, member):
        super().__init__(timeout=None)
        self.bot = bot
        self.member = member

        for role_name, role_info in ROLE_DATA.items():
            self.add_item(RoleButton(bot, member, role_name, role_info["emoji"], role_info["role_name"], role_info["role_id"]))


class RoleButton(discord.ui.Button):
    def __init__(self, bot, member, role_name, emoji, role_display_name, role_id):
        super().__init__(label=role_name, emoji=emoji, style=discord.ButtonStyle.primary)
        self.bot = bot
        self.member = member
        self.role_display_name = role_display_name
        self.role_id = role_id

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        member = self.member
        if not guild:
            await interaction.response.send_message("An error occurred. Try again.", ephemeral=True)
            return

        role = guild.get_role(self.role_id)
        if not role:
            await interaction.response.send_message("The role is unavailable.", ephemeral=True)
            return

        def_role = guild.get_role(1300093554064097401)  # DEF Role ID
        try:
            await member.add_roles(role, def_role)
            await interaction.response.send_message(f"You have been assigned **{self.role_display_name}** and **DEF** roles.", ephemeral=True)

            # Prompt for in-game name
            await member.send("Please enter your in-game name:")
            def check(msg):
                return msg.author == member and isinstance(msg.channel, discord.DMChannel)

            response = await self.bot.wait_for("message", check=check, timeout=300)
            ign = response.content

            # Update nickname
            nickname = f"[{self.role_display_name}] {ign}"
            await member.edit(nick=nickname)
            await member.send(f"Your nickname has been updated to: {nickname}")

        except discord.Forbidden:
            await interaction.response.send_message("I lack the permissions to assign roles or change nicknames.", ephemeral=True)
        except discord.HTTPException as e:
            await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)


class RoleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        member = message.author
        guild = message.guild

        if len(member.roles) <= 1:  # If the member only has the default role
            embed = discord.Embed(
                title="Welcome!",
                description="Please select your guild by clicking one of the buttons below.",
                color=discord.Color.blue(),
            )
            try:
                await member.send(embed=embed, view=RoleSelectionView(self.bot, member))
            except discord.Forbidden:
                pass


async def setup(bot):
    await bot.add_cog(RoleCog(bot))
