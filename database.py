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
