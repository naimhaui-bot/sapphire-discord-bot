import asyncio
import logging

import discord
from discord import app_commands
from discord.ext import commands

from src.config import settings
from src.database import close_database, init_database
from src.events import EventCog
from src.cogs.core import CoreCog
from src.cogs.moderation import ModerationCog
from src.cogs.welcome import WelcomeCog
from src.cogs.leveling import LevelingCog
from src.cogs.honeypot import HoneypotCog
from src.cogs.akinator import AkinatorCog
from src.cogs.roles import RoleCog

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
log = logging.getLogger("sapphire")


class SapphireBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        intents.moderation = True
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None,
            allowed_mentions=discord.AllowedMentions(
                everyone=False, users=True, roles=False, replied_user=False
            ),
        )

    async def setup_hook(self) -> None:
        await init_database()
        for cog in (
            CoreCog,
            ModerationCog,
            WelcomeCog,
            LevelingCog,
            HoneypotCog,
            AkinatorCog,
            RoleCog,
            EventCog,
        ):
            await self.add_cog(cog(self))

        if settings.command_sync_guild_id:
            guild = discord.Object(id=settings.command_sync_guild_id)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            log.info("Synced commands to guild %s", guild.id)
        else:
            await self.tree.sync()
            log.info("Synced global application commands")

    async def on_ready(self) -> None:
        if self.user:
            log.info("Logged in as %s (%s) in %d guilds", self.user, self.user.id, len(self.guilds))
        await self.change_presence(
            activity=discord.Activity(type=discord.ActivityType.watching, name="/help | Sapphire")
        )

    async def on_tree_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        if isinstance(error, app_commands.CommandOnCooldown):
            message = f"Try again in `{error.retry_after:.1f}s`."
        elif isinstance(error, app_commands.MissingPermissions):
            message = "You do not have the required Discord permissions for this command."
        elif isinstance(error, app_commands.BotMissingPermissions):
            message = "I am missing a required permission. Check my role and channel permissions."
        elif isinstance(error, app_commands.CheckFailure):
            message = "This command is not available here or you are not allowed to use it."
        else:
            log.error("Unhandled application-command error", exc_info=error)
            message = "Something went wrong while running that command."

        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)

    async def close(self) -> None:
        await close_database()
        await super().close()


async def main() -> None:
    if not settings.token:
        raise RuntimeError("DISCORD_TOKEN is required")
    bot = SapphireBot()
    try:
        await bot.start(settings.token)
    finally:
        if not bot.is_closed():
            await bot.close()


if __name__ == "__main__":
    asyncio.run(main())