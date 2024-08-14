import os
import re
import sqlite3
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

db = sqlite3.connect('bot.db', autocommit=False)
db_cur = db.cursor()

db_cur.executescript(r"""
CREATE TABLE IF NOT EXISTS variables(
  guild_id INTEGER NOT NULL,
  name,
  value,
  PRIMARY KEY (guild_id, name)
);
""")

def var_get(guild_id: int, varname: str) -> int | None:
  db_cur.execute(
    r"SELECT value FROM variables WHERE guild_id = ? AND name = ?",
    (guild_id, varname))
  res = db_cur.fetchone()
  if res:
    (value,) = res
    return value
  else:
    return None

def var_set(guild_id: int, varname: str, value: int) -> None:
  db_cur.execute(
    r"INSERT OR REPLACE INTO variables(guild_id, name, value) VALUES (?, ?, ?)",
    (guild_id, varname, value))
  db.commit()

@client.event
async def on_message(message):
  if message.author == client.user or message.author.bot:
    return

  if not message.guild:
    return
  guild_id = message.guild.id

  c = message.content
  if c.startswith('++'):
    delta = 1
    varname = c[2:]
  elif c.startswith('--'):
    delta = -1
    varname = c[2:]
  else:
    return

  if not VARNAME_REGEX.match(varname):
    return

  curr_value = var_get(guild_id, varname)
  if curr_value:
    new_value = curr_value + delta
  else:
    new_value = delta
  var_set(guild_id, varname, new_value)

  await message.reply(f"{varname} = {new_value}")

client.run(client_token)
