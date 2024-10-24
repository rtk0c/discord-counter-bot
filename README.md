# Discord Counter Bot

A Discord bot for, well, having counters. Count with plain messages like `variable++`, or slash commands `/inc` and `/dec` with autocomplete.
A picture is word a thousand words.

![counting](https://github.com/user-attachments/assets/2958eb5e-9fef-41cf-883c-ad4e9458c90d)
![autocomplete](https://github.com/user-attachments/assets/f0f4fb80-cb62-451e-943d-20b237505923)

You can search for variables in the current guild with the `/list` command.

![searching](https://github.com/user-attachments/assets/0930bb6d-17d1-4ee9-8556-db3b34d0e78e)

This is heavily inspired by tterrag's [K9](https://www.tterrag.com/k9)'s counting functionality. But extended with slash commands and more convenience!

## Deployment
- Register a Discord app (example: [discord.py help](https://discordpy.readthedocs.io/en/latest/discord.html)), and invite it to your servers with permissions Send Messages and Read Message History.
- Install discord.py
- Clone this repository
- Set env var `DISCORD_BOT_TOKEN=<your bot token>`
- `python main.py`
  - Variable data will be stored in a SQLite file `bot.db` in cwd, keep good care of it.
