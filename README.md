# Sapphire

Sapphire is a modular, production-oriented Discord moderation, welcome, leveling,
anti-raid, and interactive game bot built with Python and `discord.py`.

## Features

- Slash commands with permission and role-hierarchy checks
- Moderation cases, warnings, timeout, kick, ban, user information, and logs
- Per-server welcome, goodbye, embeds, DMs, auto-role, and message variables
- Persistent Arcane-style XP, levels, cooldowns, leaderboards, and staff XP tools
- Honeypot channels, join-rate anti-raid protection, lockdown, and whitelist bypasses
- Akinator-style interactive character game with buttons and persistent statistics
- SQLite storage through SQLAlchemy and `aiosqlite`
- Graceful shutdown, structured logging, environment-only secrets, and CI

## Requirements

- Python 3.11+
- A Discord application with a bot user
- Message Content and Server Members privileged intents enabled in the Discord Developer Portal

## Local installation

```bash
git clone https://github.com/naimhaui-bot/sapphire-discord-bot.git
cd sapphire-discord-bot
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set `DISCORD_TOKEN` in `.env`, then start:

```bash
python bot.py
```

Sapphire uses a local SQLite database named `sapphire.sqlite3`.

Invite the bot with the `bot` and `applications.commands` scopes. Required
permissions depend on enabled features: View Channels, Send Messages, Embed
Links, Read Message History, Manage Messages, Moderate Members, Kick Members,
Ban Members, and Manage Roles.

## Commands

- Core: `/help`, `/settings`, `/logchannel`, `/customcommand`
- Moderation: `/warn`, `/timeout`, `/kick`, `/ban`, `/case`, `/userinfo`, `/serverinfo`
- Welcome: `/welcome`, `/goodbye`, `/autorole`, `/welcomedm`
- Arcane: `/rank`, `/levels`, `/leaderboard`, `/setlevel`, `/addxp`, `/removexp`
- Honeypot: `/honeypot`, `/raid`, `/whitelist`, `/lockdown`
- Game: `/akinator`, `/akinatorstats`, `/akinatorleaderboard`

Welcome variables are `{user}`, `{username}`, `{server}`, `{memberCount}`, and
`{mention}`. Unknown variables remain unchanged.

## Wisbyte deployment

1. Create a Python application or service in Wisbyte and connect this GitHub repository.
2. Use Python 3.11 or newer.
3. Install dependencies with `pip install -r requirements.txt`.
4. Set the startup command to `python bot.py`.
5. Configure only these environment variables:

| Variable | Required | Description |
|---|---:|---|
| `DISCORD_TOKEN` | Yes | Token of the Discord bot application. |
| `CLIENT_ID` | No | Discord application client ID. |
| `CLIENT_SECRET` | No | Discord application client secret. |

The bot uses the local SQLite file `sapphire.sqlite3`. Enable persistent storage in Wisbyte if the database must survive restarts or redeployments. Restart the service and check the logs for `Database initialized` and `Synced global application commands`.

Sapphire has no hard-coded paths, opens one managed database engine, handles SIGTERM
through the asyncio process lifecycle, and closes the database pool during shutdown.

## Security

Secrets are never committed; `.env` is ignored. The bot validates user-controlled
lengths, checks Discord permissions and role hierarchy, excludes administrators,
owners, and whitelisted users from automated punishment, and sets restrictive
allowed mentions. Keep the bot role below server-owner/admin roles and enable only
the permissions required by your server.
