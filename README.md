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
- Local SQLite storage through SQLAlchemy and `aiosqlite`
- Graceful shutdown, structured logging, environment-only secrets, and CI

## Requirements

- Python 3.11+
- A Discord application with a bot user
- PostgreSQL 14+ for production
- Message Content and Server Members privileged intents enabled in the Discord Developer Portal

## Local installation

```bash
git clone https://github.com/your-org/sapphire.git
cd sapphire
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set `DISCORD_TOKEN`, `CLIENT_ID`, and `CLIENT_SECRET` in Wispbyte, then start:

```bash
python bot.py
```

Sapphire uses the local SQLite file `sapphire.sqlite3`; no database variable is required.

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

1. Use the `python_3.11` Docker image.
2. Connect the public GitHub repository.
3. Set the main file to `bot.py`.
4. Use `python bot.py` as the startup command.
5. Install dependencies with `pip install -r requirements.txt`.
6. Configure only `DISCORD_TOKEN`, `CLIENT_ID`, and `CLIENT_SECRET` in Environment.
7. Restart after saving the variables and inspect the application logs for `Sapphire is ready`.

Sapphire has no hard-coded paths, opens one managed database engine, handles SIGTERM
through the asyncio process lifecycle, and closes the database pool during shutdown.

## Security

Secrets are never committed; `.env` is ignored. The bot validates user-controlled
lengths, checks Discord permissions and role hierarchy, excludes administrators,
owners, and whitelisted users from automated punishment, and sets restrictive
allowed mentions. Keep the bot role below server-owner/admin roles and enable only
the permissions required by your server.

## GitHub

A minimal CI workflow is included in `.github/workflows/ci.yml`. It validates Python
syntax and dependency installation without requiring Discord credentials or a live
database.