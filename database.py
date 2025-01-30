import psycopg2
import os

# Supabase connection details
DATABASE_URL = os.getenv("DATABASE_URL")  # Get the connection URL from environment variables

def initialize_db():
    """Initialize the database and create the table if it doesn't exist."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS guilds (
                id SERIAL PRIMARY KEY,
                guild_name TEXT NOT NULL UNIQUE,
                emoji_id TEXT NOT NULL,
                role_id TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()
        print("Database initialized successfully.")
    except psycopg2.Error as e:
        print(f"Error initializing database: {e}")
        raise

def add_guild(guild_name: str, emoji_id: str, role_id: str):
    """Add a new guild to the database."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO guilds (guild_name, emoji_id, role_id)
            VALUES (%s, %s, %s)
        """, (guild_name, emoji_id, role_id))
        conn.commit()
        conn.close()
    except psycopg2.Error as e:
        print(f"Error adding guild: {e}")
        raise

def delete_guild(guild_name: str):
    """Delete a guild from the database."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM guilds WHERE guild_name = %s
        """, (guild_name,))
        conn.commit()
        conn.close()
    except psycopg2.Error as e:
        print(f"Error deleting guild: {e}")
        raise

def get_all_guilds():
    """Fetch all guilds from the database."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM guilds")
        guilds = cursor.fetchall()
        conn.close()
        return guilds
    except psycopg2.Error as e:
        print(f"Error fetching guilds: {e}")
        raise

def get_guild_by_name(guild_name: str):
    """Fetch a specific guild by name."""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM guilds WHERE guild_name = %s", (guild_name,))
        guild = cursor.fetchone()
        conn.close()
        return guild
    except psycopg2.Error as e:
        print(f"Error fetching guild: {e}")
        raise
