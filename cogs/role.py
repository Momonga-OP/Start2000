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
        super().__init__(timeout=None)  # No timeout
        self.bot = bot
        self.member = member

        # Add a button for each role
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
        """Assigns or creates the selected role and prompts for in-game name."""
        server = interaction.guild or self.member.guild
        user = self.member

        if not server:
            await interaction.response.send_message("Une erreur s'est produite. Veuillez réessayer.", ephemeral=True)
            return

        # Get or create the role
        role = server.get_role(self.role_id)
        if not role:
            try:
                role = await server.create_role(
                    name=self.role_display_name,
                    reason="Création automatique de rôle via panel de sélection."
                )
            except discord.Forbidden:
                await interaction.response.send_message("Je n'ai pas la permission de créer un rôle.", ephemeral=True)
                return

        try:
            await user.add_roles(role, reason="Rôle assigné via le panel de sélection.")
            await interaction.response.send_message(
                f"Vous avez reçu le rôle **{self.role_display_name}** avec succès !", ephemeral=True
            )
            # Prompt for in-game name
            await self.ask_for_ign(user)
        except discord.Forbidden:
            await interaction.response.send_message("Je n'ai pas la permission d'assigner ce rôle.", ephemeral=True)
        except discord.HTTPException as e:
            await interaction.response.send_message(f"Erreur lors de l'attribution du rôle : {e}", ephemeral=True)

    async def ask_for_ign(self, user: discord.Member):
        """Sends a message asking for the in-game name."""
        try:
            await user.send(
                "Pour compléter votre inscription, veuillez entrer votre nom en jeu :"
            )

            def check(message: discord.Message):
                return message.author == user and isinstance(message.channel, discord.DMChannel)

            response = await self.bot.wait_for("message", check=check, timeout=300)  # Wait for 5 minutes
            await user.send(f"Merci ! Votre nom en jeu **{response.content}** a été enregistré.")
        except discord.Forbidden:
            print(f"Impossible d'envoyer un DM à {user.name}. Les DM sont peut-être désactivés.")
        except TimeoutError:
            await user.send("Temps écoulé ! Veuillez réessayer de fournir votre nom en jeu plus tard.")


class RoleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Detects a new user when they send their first message."""
        if message.author.bot:
            return  # Ignore bots

        user = message.author
        server = message.guild

        if server is None:
            return  # Ignore DMs

        # Check if the user has only the default role
        if len(user.roles) <= 1:
            await self.send_welcome_message(user)

    async def send_welcome_message(self, member: discord.Member):
        """Sends a welcome DM to the new user with role selection buttons."""
        embed = discord.Embed(
            title="Bienvenue dans l'Alliance !",
            description=(
                "Bienvenue sur le serveur ! Veuillez choisir votre rôle parmi les options ci-dessous en cliquant sur un bouton. "
                "Votre rôle déterminera votre place dans l'alliance. Faites le bon choix !"
            ),
            color=discord.Color.blue()
        )
        embed.set_footer(text="Panel de sélection des rôles")
        embed.set_thumbnail(url=member.guild.icon.url if member.guild.icon else None)

        try:
            await member.send(
                content="Bienvenue sur le serveur !",
                embed=embed,
                view=RoleSelectionView(self.bot, member)
            )
        except discord.Forbidden:
            print(f"Impossible d'envoyer un DM à {member.name}. Les DM sont peut-être désactivés.")


async def setup(bot):
    await bot.add_cog(RoleCog(bot))
