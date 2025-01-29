from .database import get_all_guilds

# Configuration
GUILD_ID = 1300093554064097400  # Replace with your guild ID
PING_DEF_CHANNEL_ID = 1307429490158342256  # Replace with your ping channel ID
ALERTE_DEF_CHANNEL_ID = 1300093554399645715  # Replace with your alert channel ID

# French alert messages
ALERT_MESSAGES = [
    "🚨 {role} go def zebi !",
    "⚔️ {role}, il est temps de défendre !",
    "🛡️ {role} Défendez votre guilde !",
    "💥 {role} est attaquée ! Rejoignez la défense !",
    "⚠️ {role}, mobilisez votre équipe pour défendre !",
    "🏹 Appel urgent pour {role} - La défense a besoin de vous !",
    "🔔 {role}, votre présence est cruciale pour la défense !",
]

def get_guild_emojis_roles():
    """Fetch guild data from the database."""
    guilds = get_all_guilds()
    return {
        guild[1]: {"emoji": guild[2], "role_id": guild[3]}  # guild_name: {emoji, role_id}
        for guild in guilds
    }
