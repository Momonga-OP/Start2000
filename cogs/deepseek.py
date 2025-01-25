import discord
from discord.ext import commands
from openai import OpenAI

class DeepSeekCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Initialize the OpenAI client with your API key
        self.client = OpenAI(api_key="DEEPSEEK_TOKEN", base_url="https://api.deepseek.com")
        # Replace with your bot's ID
        self.BOT_ID = 1309408833818333264

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore messages from the bot itself
        if message.author == self.bot.user:
            return

        # Check if the bot is tagged in the message
        if f"<@{self.BOT_ID}>" in message.content:
            # Extract the user's message content (remove the bot tag)
            user_message = message.content.replace(f"<@{self.BOT_ID}>", "").strip()

            # Send the user's message to the DeepSeek API
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant"},
                    {"role": "user", "content": user_message},
                ],
                stream=False
            )

            # Get the bot's response
            bot_response = response.choices[0].message.content

            # Send the bot's response back to the Discord channel
            await message.channel.send(bot_response)

# This function is required to add the cog to the bot
async def setup(bot):
    await bot.add_cog(DeepSeekCog(bot))
