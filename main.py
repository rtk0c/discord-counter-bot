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
  print(f"var_set({guild_id}, '{varname}', {value})")

def var_search(guild_id: int, varname_pattern: str) -> list[(str, int)]:
  db_cur.execute(
    fr"SELECT name, value FROM variables WHERE guild_id = ? AND name LIKE ?",
    (guild_id, f"%{varname_pattern}%"))
  res = db_cur.fetchall()
  print(f"var_search({guild_id}, '{varname_pattern}') = ", res)
  return res

# https://gist.github.com/lykn/bac99b06d45ff8eed34c2220d86b6bf4
class ListCmdView(discord.ui.View):
  def __init__(self, guild_id, search_term, *, timeout=180):
    super().__init__(timeout=timeout)
    self.guild_id = guild_id
    self.search_term = search_term
    self.search_result = var_search(guild_id, search_term)
    # The next entry from self.search_result that should be displayed to the user,
    # because it was cut off due to Discord's message length limit
    self.idx = 0

  def search_next(self):
    content_footer = ['```']
    content = []
    content_len = sum((len(s) + 1 for s in content_footer))
    def append_line(s):
      nonlocal content_len, content
      content_len += len(s) + 1 # Line break
      # Discord's message length limit, minus a bit of room
      # In testing, messages /right/ below 2000 seems to be flaky? Not sure why.
      if content_len > 1950:
        return False
      content.append(s)
      return True
    append_line(f"Variables with name containing: {self.search_term}")
    append_line('```')

    while True:
      # Until: no more search results
      if self.idx >= len(self.search_result):
        self.disable_buttons()
        break
      # Until: cannot fit into this message anymore
      (name, value) = self.search_result[self.idx]
      if not append_line(f"{name} = {value}"):
        break
      self.idx += 1

    return '\n'.join(content + content_footer)

  def disable_buttons(self):
    for item in self.children:
      item.disabled = True

  @discord.ui.button(label="Next page", style=discord.ButtonStyle.gray)
  async def next(self, intr: discord.Interaction, button: discord.ui.Button):
    # self.search_next() updates button states, pass view=self to send changes to client
    await intr.response.edit_message(content=self.search_next(), view=self)

@tree.command(
  name='list',
  description='Search counters on this server matching the pattern.',
  guild=None, # Global slash command
)
async def list(intr: discord.Interaction, search_term: str):
  view = ListCmdView(intr.guild_id, search_term)
  await intr.response.send_message(content=view.search_next(), view=view, ephemeral=True)

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
