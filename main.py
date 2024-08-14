import os
import re
import discord

# Let it throw error and crash if the env does not exist
client_token = os.environ['DISCORD_BOT_TOKEN']

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
  pass

# Additionally allow dashes, because that's convenient
VARNAME_REGEX = re.compile(r"[a-zA-Z0-9_-]+")

@client.event
async def on_message(message):
  if message.author == client.user or message.author.bot:
    return

  c = message.content
  if not c.startswith('++') and not c.startswith('--'):
    return
  rest = c[2:]
  if not VARNAME_REGEX.match(rest):
    return

  print(f"recieved {rest}")
  await message.reply(f"{rest} = 10")

client.run(client_token)
