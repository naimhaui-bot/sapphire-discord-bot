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
- PostgreSQL storage through SQLAlchemy, with SQLite available for local development
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

Set `DISCORD_TOKEN` and `DATABASE_URL` in `.env`, then start:

```bash
python bot.py
```

`DATABASE_URL` accepts SQLAlchemy async URLs. For PostgreSQL use
`postgresql+asyncpg://user:password@host:5432/database`. If it is omitted,
Sapphire uses a local SQLite file for development only.

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

## PostgreSQL setup

```sql
CREATE USER sapphire WITH PASSWORD 'use-a-long-random-password';
CREATE DATABASE sapphire OWNER sapphire;
```

Set the resulting connection string in `DATABASE_URL`. Tables are created on
startup. For larger teams, add Alembic migrations before changing production
schemas.

## Wisbyte deployment

1. Create a Python application/service in Wisbyte.
2. Upload the repository or connect the GitHub repository.
3. Use Python 3.11 or newer.
4. Set the startup command to `python bot.py`.
5. Add every variable from `.env.example` in the Wisbyte environment settings.
6. Set `DATABASE_URL` to the Wisbyte PostgreSQL connection string.
7. Install dependencies with `pip install -r requirements.txt` as the build/install command.
8. Enable persistent storage only for local SQLite development; production data belongs in PostgreSQL.
9. Restart after saving variables and inspect the application logs for `Database initialized`
   and `Synced global application commands`.

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