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

DEF_ROLE_ID = 1300093554064097401  # Default DEF role ID


class RoleSelectionView(discord.ui.View):
    def __init__(self, bot, member):
        super().__init__(timeout=None)
        self.bot = bot
        self.member = member

        for role_name, role_info in ROLE_DATA.items():
            self.add_item(
                RoleButton(
                    bot,
                    member,
                    role_name,
                    role_info["emoji"],
                    role_info["role_name"],
                    role_info["role_id"],
                )
            )


class RoleButton(discord.ui.Button):
    def __init__(self, bot, member, role_name, emoji, role_display_name, role_id):
        super().__init__(label=role_name, emoji=emoji, style=discord.ButtonStyle.primary)
        self.bot = bot
        self.member = member
        self.role_display_name = role_display_name
        self.role_id = role_id

    async def callback(self, interaction: discord.Interaction):
        server = interaction.guild or self.member.guild
        user = self.member

        if not server:
            await interaction.response.send_message(
                "An error occurred. Please try again.", ephemeral=True
            )
            return

        role = server.get_role(self.role_id)
        if not role:
            role = await server.create_role(
                name=self.role_display_name,
                reason="Auto-created role via selection panel."
            )

        def_role = server.get_role(DEF_ROLE_ID)
        if not def_role:
            await interaction.response.send_message(
                "The DEF role does not exist on the server. Please contact an admin.",
                ephemeral=True,
            )
            return

        try:
            await user.add_roles(role, def_role, reason="Roles assigned via selection panel.")
            await interaction.response.send_message(
                f"You've been assigned the **{self.role_display_name}** and **DEF** roles successfully!",
                ephemeral=True,
            )

            await self.ask_for_ign(user, self.role_display_name)
        except discord.Forbidden:
            await interaction.response.send_message(
                "I don't have permission to assign roles.", ephemeral=True
            )

    async def ask_for_ign(self, user: discord.Member, guild_name: str):
        try:
            await user.send("Please enter your in-game name:")

            def check(message: discord.Message):
                return (
                    message.author == user
                    and isinstance(message.channel, discord.DMChannel)
                )

            response = await self.bot.wait_for("message", check=check, timeout=300)
            new_nickname = f"[{guild_name}] {response.content}"

            try:
                await user.edit(nick=new_nickname, reason="Updated nickname to in-game name.")
                await user.send(
                    f"Thank you! Your in-game name has been set to **{new_nickname}**."
                )
            except discord.Forbidden:
                await user.send(
                    "I couldn't change your nickname due to missing permissions. Please inform an admin."
                )
        except discord.Forbidden:
            print(f"Unable to DM {user.name}.")
        except TimeoutError:
            await user.send(
                "Timeout! Please try providing your in-game name later."
            )


class RoleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        user = message.author
        server = message.guild

        if server is None:
            return

        if len(user.roles) <= 1:
            await self.send_welcome_message(user)

    async def send_welcome_message(self, member: discord.Member):
        embed = discord.Embed(
            title="Welcome to the Alliance!",
            description=(
                "Welcome to the server! Please select your role by clicking a button below. "
                "Your role determines your place in the alliance. Choose wisely!"
            ),
            color=discord.Color.blue(),
        )
        embed.set_footer(text="Role selection panel")
        embed.set_thumbnail(url=member.guild.icon.url if member.guild.icon else None)

        try:
            await member.send(
                content="Welcome to the server!",
                embed=embed,
                view=RoleSelectionView(self.bot, member),
            )
        except discord.Forbidden:
            print(f"Unable to DM {member.name}. DMs might be disabled.")


async def setup(bot):
    await bot.add_cog(RoleCog(bot))
