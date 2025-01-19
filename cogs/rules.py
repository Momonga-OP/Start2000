import discord
from discord.ext import commands

class Rules(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.rules_channel_id = 1300093554399645708  # Channel ID where rules are posted
        self.role_to_assign = 1330547847720079450  # Role ID to assign when users agree
        self.rules_content = (
            "**R\u00e8glement du Serveur Discord de l’Alliance [START]**\n\n"
            "Bienvenue à tous les membres de l’Alliance ! Afin de garantir une expérience de jeu égéable et productive, voici les règles à respecter sur ce serveur :\n\n"
            "**Respect et bonne entente**\n"
            "Le respect mutuel est la clé d’une communauté saine. Tout comportement irrespectueux, injurieux, discriminatoire ou offensant est strictement interdit.\n"
            "Évitez les conflits inutiles et privilégiez la communication pour résoudre les désaccords.\n\n"
            "**L’entraide avant tout**\n"
            "L’entraide est une valeur essentielle de notre alliance. N’hésitez pas à proposer votre aide aux membres en difficulté (succès, donjons, quêtes, ressources).\n"
            "Partagez vos connaissances et astuces avec bienveillance.\n\n"
            "**Importance des défenses (PING DEF)**\n"
            "Chaque membre se doit d’être réactif lorsqu’une alerte DEF est signalée.\n"
            "Lorsqu’un ping DEF est envoyé, utilisez le bon canal et ajoutez une note au ping précisant quelle guilde/alliance nous attaquent.\n"
            "Ces informations sont indispensables pour organiser une défense efficace et cibler les ennemis en cas de vengeance.\n\n"
            "**Communication claire**\n"
            "Les annonces importantes doivent être respectées, et les discussions doivent rester dans les canaux appropriés.\n"
            "Le spam, les pings inutiles et les messages répétitifs sont interdits.\n\n"
            "**Gestion des ressources communes**\n"
            "Toute demande d’objets, ressources ou services doit passer par les canaux dédiés.\n"
            "Les échanges commerciaux se font dans le respect des prix raisonnables définis par l’alliance.\n\n"
            "**Confidentialité des informations**\n"
            "Les informations stratégiques de l’alliance ne doivent jamais être divulguées à des tiers, même après avoir quitté l’alliance.\n\n"
            "**Participation aux activités de l’alliance**\n"
            "La présence régulière lors des événements, défenses, et autres activités est encouragée pour le bon fonctionnement de l’alliance.\n"
            "L'inaction répétée lors des pings importants pourra mener à revoir votre engagement vis à vis de l'alliance.\n\n"
            "---\n"
            "**Sanctions**\n"
            "Le non-respect des règles entraînera des sanctions allant d’un simple avertissement à une exclusion définitive du serveur selon la gravité de l’infraction.\n\n"
            "---\n"
            "En acceptant de rejoindre ce serveur, vous vous engagez à respecter ces règles et à contribuer à un environnement positif et dynamique. Bonne aventure à tous !"
        )

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.bot.user} is ready and Rules Cog is active!")
        await self.post_rules()

    async def post_rules(self):
        channel = self.bot.get_channel(self.rules_channel_id)
        if not channel:
            print("Rules channel not found. Please check the ID.")
            return

        embed = discord.Embed(
            title="R\u00e8glement du Serveur Discord de l’Alliance [START]",
            description=self.rules_content,
            color=discord.Color.blue()
        )
        embed.set_footer(text="Veuillez réagir pour accepter les règles et obtenir l’accès au serveur.")

        await channel.purge(limit=10)  # Clear old messages
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
