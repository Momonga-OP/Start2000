from .database import get_all_guilds

def get_guild_emojis_roles():
    """Fetch guild data from the database."""
    guilds = get_all_guilds()
    return {
        guild[1]: {"emoji": guild[2], "role_id": guild[3]}  # guild_name: {emoji, role_id}
        for guild in guilds
    }
