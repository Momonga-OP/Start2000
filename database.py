import sqlite3

DATABASE_PATH = "guilds.db"

def initialize_db():
    """Initialize the database and create the table if it doesn't exist."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS guilds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_name TEXT NOT NULL UNIQUE,
            emoji_id TEXT NOT NULL,
            role_id TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def add_guild(guild_name: str, emoji_id: str, role_id: str):
    """Add a new guild to the database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO guilds (guild_name, emoji_id, role_id)
        VALUES (?, ?, ?)
    """, (guild_name, emoji_id, role_id))
    conn.commit()
    conn.close()

def delete_guild(guild_name: str):
    """Delete a guild from the database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM guilds WHERE guild_name = ?
    """, (guild_name,))
    conn.commit()
    conn.close()

def get_all_guilds():
    """Fetch all guilds from the database."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM guilds")
    guilds = cursor.fetchall()
    conn.close()
    return guilds

def get_guild_by_name(guild_name: str):
    """Fetch a specific guild by name."""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM guilds WHERE guild_name = ?", (guild_name,))
    guild = cursor.fetchone()
    conn.close()
    return guild
