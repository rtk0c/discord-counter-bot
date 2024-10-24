import os
import re
import sqlite3
import discord

# Let it throw error and crash if the env does not exist
client_token = os.environ['DISCORD_BOT_TOKEN']

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

VARNAME_REGEX = re.compile(r"[a-zA-Z0-9_]+")

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

@tree.command(
    name='list',
    description='List all counters present on this server',
    guild=None, # Global slash command
)
async def list(intr: discord.Interaction, search_term: str):
    await intr.response.send_message(search_term)
    return
    current_page = 0
    embed = generate_embed(current_page)
    
    message = await ctx.send(embed=embed)

    while True:
        try:
            reaction, user = await client.wait_for('reaction_add', check=lambda r, u: u == ctx.author 
and str(r.emoji) in ['<<', '>>'], timeout=60.0)
        except asyncio.TimeoutError:
            break

        if str(reaction.emoji) == '<<':
            current_page = max(current_page - 1, 0)
        elif str(reaction.emoji) == '>>':
            current_page = min(current_page + 1, len(numbers_list) // NUMBERS_PER_PAGE)

        await message.edit(embed=generate_embed(current_page))
        await reaction.remove(user)

def generate_embed(page):
    start_index = page * NUMBERS_PER_PAGE
    end_index = start_index + NUMBERS_PER_PAGE

    current_numbers = numbers_list[start_index:end_index]
    embed = discord.Embed(title=f"Page {page + 1}", description="\n".join(map(str, 
current_numbers)))
    if page > 0:
        embed.add_field(name="<<", value="Previous Page", inline=False)
    if end_index < len(numbers_list):
        embed.add_field(name=">>", value="Next Page", inline=False)

    return embed

@client.event
async def on_message(message):
  if message.author == client.user or message.author.client:
    return

  if not message.guild:
    return
  guild_id = message.guild.id

  c = message.content
  if (varname := c.removeprefix('++')) != c or \
     (varname := c.removesuffix('++')) != c:
    delta = 1
  elif (varname := c.removeprefix('--')) != c or \
       (varname := c.removesuffix('--')) != c:
    delta = -1
  else:
    return

  if not VARNAME_REGEX.fullmatch(varname):
    return

  curr_value = var_get(guild_id, varname)
  if curr_value:
    new_value = curr_value + delta
  else:
    new_value = delta
  var_set(guild_id, varname, new_value)

  await message.reply(f"{varname} = {new_value}", mention_author=False)

@client.event
async def on_ready():
  await tree.sync()
  print('ready')

client.run(client_token)
