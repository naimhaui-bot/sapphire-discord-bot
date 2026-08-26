import discord
from discord import app_commands
from discord.ext import commands
from sqlalchemy import select

from src.database import SessionLocal
from src.models import GuildConfig
from src.services.settings import get_config, update_config
from src.utils.checks import administrator
from src.utils.embeds import embed, success, warning


class CoreCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="help", description="Show Sapphire's command guide.")
    async def help(self, interaction: discord.Interaction) -> None:
        message = (
            "**Moderation:** `/warn` `/timeout` `/kick` `/ban` `/case` `/userinfo`\n"
            "**Welcome:** `/welcome` `/goodbye` `/autorole`\n"
            "**Arcane:** `/rank` `/leaderboard` `/setlevel` `/addxp` `/removexp`\n"
            "**Honeypot:** `/honeypot` `/raid` `/whitelist` `/lockdown`\n"
            "**Games:** `/akinator`\n\n"
            "Administrators can use `/settings` to view server configuration."
        )
        await interaction.response.send_message(embed=embed("Sapphire command guide", message), ephemeral=True)

    @app_commands.command(name="settings", description="View this server's active configuration.")
    @administrator()
    async def settings_command(self, interaction: discord.Interaction) -> None:
        assert interaction.guild
        async with SessionLocal() as database:
            config = await get_config(database, interaction.guild.id)
        await interaction.response.send_message(
            embed=embed(
                "Server settings",
                f"Welcome: {'on' if config.welcome_enabled else 'off'}\n"
                f"Goodbye: {'on' if config.goodbye_enabled else 'off'}\n"
                f"XP rate: `{config.xp_rate:g}` · XP cooldown: `{config.xp_cooldown}s`\n"
                f"Honeypot: {f'<#{config.honeypot_channel_id}>' if config.honeypot_channel_id else 'off'}\n"
                f"Raid protection: `{config.raid_threshold}` joins / `{config.raid_window}s`",
            ),
            ephemeral=True,
        )

    @app_commands.command(name="logchannel", description="Set or clear the moderation log channel.")
    @app_commands.describe(channel="Channel for moderation logs; omit to disable.")
    @administrator()
    async def logchannel(self, interaction: discord.Interaction, channel: discord.TextChannel | None = None) -> None:
        assert interaction.guild
        async with SessionLocal() as database:
            await update_config(database, interaction.guild.id, moderation_log_channel_id=channel.id if channel else None)
        await interaction.response.send_message(
            embed=success("Moderation logs updated", f"Logs: {channel.mention if channel else 'disabled'}"),
            ephemeral=True,
        )

    @app_commands.command(name="customcommand", description="Create, update, or delete a custom text command.")
    @app_commands.describe(name="Command name", response="Response text; leave empty to delete.")
    @administrator()
    async def customcommand(self, interaction: discord.Interaction, name: str, response: str | None = None) -> None:
        assert interaction.guild
        name = name.lower().strip()
        if not name.isalnum() or len(name) > 32:
            await interaction.response.send_message("The command name must be 1–32 letters or numbers.", ephemeral=True)
            return
        async with SessionLocal() as database:
            config = await get_config(database, interaction.guild.id)
            commands_map = dict(config.custom_commands or {})
            if response:
                if len(response) > 2000:
                    await interaction.response.send_message("The response cannot exceed 2,000 characters.", ephemeral=True)
                    return
                commands_map[name] = response
            else:
                commands_map.pop(name, None)
            await update_config(database, interaction.guild.id, custom_commands=commands_map)
        action = "saved" if response else "deleted"
        await interaction.response.send_message(embed=success("Custom command updated", f"`{name}` was {action}."), ephemeral=True)