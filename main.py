import os
import discord

# Let it throw error and crash if the env does not exist
client_token = os.environ['DISCORD_BOT_TOKEN']

class MyClient(discord.Client):
    async def on_ready(self):
        pass

    async def on_message(self, message):
        pass

intents = discord.Intents.default()
intents.message_content = True

client = MyClient(intents=intents)
client.run(client_token)
