import discord
from discord import app_commands
from discord.ext import commands
import requests

class DofusTouch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Function to fetch data from DOFAPI
    def fetch_dofus_data(self, category, name):
        url = f"https://api.dofapi.dev/{category}?name={name}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data:
                return data[0]  # Return the first matching item
        return None

    # Function to format the API response
    def format_response(self, data):
        name = data.get("name", "Unknown")
        description = data.get("description", "No description available.")
        image_url = data.get("imgUrl", "")
        response = f"**{name}**\n{description}"
        if image_url:
            response += f"\n{image_url}"
        return response

    # Slash command: /equipment <name>
    @app_commands.command(name="equipment", description="Fetch equipment data from DOFAPI")
    @app_commands.describe(name="The name of the equipment")
    async def equipment(self, interaction: discord.Interaction, name: str):
        data = self.fetch_dofus_data("equipment", name)
        if data:
            await interaction.response.send_message(self.format_response(data))
        else:
            await interaction.response.send_message(f"Equipment '{name}' not found.")

    # Slash command: /weapon <name>
    @app_commands.command(name="weapon", description="Fetch weapon data from DOFAPI")
    @app_commands.describe(name="The name of the weapon")
    async def weapon(self, interaction: discord.Interaction, name: str):
        data = self.fetch_dofus_data("weapons", name)
        if data:
            await interaction.response.send_message(self.format_response(data))
        else:
            await interaction.response.send_message(f"Weapon '{name}' not found.")

    # Slash command: /set <name>
    @app_commands.command(name="set", description="Fetch set data from DOFAPI")
    @app_commands.describe(name="The name of the set")
    async def set(self, interaction: discord.Interaction, name: str):
        data = self.fetch_dofus_data("sets", name)
        if data:
            await interaction.response.send_message(self.format_response(data))
        else:
            await interaction.response.send_message(f"Set '{name}' not found.")

    # Slash command: /pet <name>
    @app_commands.command(name="pet", description="Fetch pet data from DOFAPI")
    @app_commands.describe(name="The name of the pet")
    async def pet(self, interaction: discord.Interaction, name: str):
        data = self.fetch_dofus_data("pets", name)
        if data:
            await interaction.response.send_message(self.format_response(data))
        else:
            await interaction.response.send_message(f"Pet '{name}' not found.")

    # Slash command: /mount <name>
    @app_commands.command(name="mount", description="Fetch mount data from DOFAPI")
    @app_commands.describe(name="The name of the mount")
    async def mount(self, interaction: discord.Interaction, name: str):
        data = self.fetch_dofus_data("mounts", name)
        if data:
            await interaction.response.send_message(self.format_response(data))
        else:
            await interaction.response.send_message(f"Mount '{name}' not found.")

    # Slash command: /resource <name>
    @app_commands.command(name="resource", description="Fetch resource data from DOFAPI")
    @app_commands.describe(name="The name of the resource")
    async def resource(self, interaction: discord.Interaction, name: str):
        data = self.fetch_dofus_data("resources", name)
        if data:
            await interaction.response.send_message(self.format_response(data))
        else:
            await interaction.response.send_message(f"Resource '{name}' not found.")

    # Slash command: /consumable <name>
    @app_commands.command(name="consumable", description="Fetch consumable data from DOFAPI")
    @app_commands.describe(name="The name of the consumable")
    async def consumable(self, interaction: discord.Interaction, name: str):
        data = self.fetch_dofus_data("consumables", name)
        if data:
            await interaction.response.send_message(self.format_response(data))
        else:
            await interaction.response.send_message(f"Consumable '{name}' not found.")

    # Slash command: /profession <name>
    @app_commands.command(name="profession", description="Fetch profession data from DOFAPI")
    @app_commands.describe(name="The name of the profession")
    async def profession(self, interaction: discord.Interaction, name: str):
        data = self.fetch_dofus_data("professions", name)
        if data:
            await interaction.response.send_message(self.format_response(data))
        else:
            await interaction.response.send_message(f"Profession '{name}' not found.")

# Cog setup function
async def setup(bot):
    await bot.add_cog(DofusTouch(bot))
