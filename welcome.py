import discord
from discord import app_commands
from discord.ext import commands

from src.database import SessionLocal
from src.services.settings import get_config, update_config
from src.utils.checks import administrator
from src.utils.embeds import embed, success
from src.utils.formatting import render


class WelcomeCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="welcome", description="Configure the welcome channel and message.")
    @app_commands.describe(channel="Welcome channel; omit to disable", message="Message using {mention}, {server}, {memberCount}, etc.")
    @administrator()
    async def welcome(self, interaction: discord.Interaction, channel: discord.TextChannel | None = None, message: str | None = None) -> None:
        assert interaction.guild
        async with SessionLocal() as database:
            values = {"welcome_enabled": channel is not None, "welcome_channel_id": channel.id if channel else None}
            if message:
                values["welcome_message"] = message[:2000]
            await update_config(database, interaction.guild.id, **values)
        await interaction.response.send_message(embed=success("Welcome system updated", f"Channel: {channel.mention if channel else 'disabled'}"), ephemeral=True)

    @app_commands.command(name="goodbye", description="Configure the goodbye channel and message.")
    @app_commands.describe(channel="Goodbye channel; omit to disable", message="Goodbye message using server variables")
    @administrator()
    async def goodbye(self, interaction: discord.Interaction, channel: discord.TextChannel | None = None, message: str | None = None) -> None:
        assert interaction.guild
        async with SessionLocal() as database:
            values = {"goodbye_enabled": channel is not None, "goodbye_channel_id": channel.id if channel else None}
            if message:
                values["goodbye_message"] = message[:2000]
            await update_config(database, interaction.guild.id, **values)
        await interaction.response.send_message(embed=success("Goodbye system updated", f"Channel: {channel.mention if channel else 'disabled'}"), ephemeral=True)

    @app_commands.command(name="autorole", description="Set the role automatically given to new members.")
    @app_commands.describe(role="Role to assign; omit to disable")
    @administrator()
    async def autorole(self, interaction: discord.Interaction, role: discord.Role | None = None) -> None:
        assert interaction.guild
        if role and interaction.guild.me and role >= interaction.guild.me.top_role:
            await interaction.response.send_message("My highest role must be above the auto-role.", ephemeral=True)
            return
        async with SessionLocal() as database:
            await update_config(database, interaction.guild.id, autorole_id=role.id if role else None)
        await interaction.response.send_message(embed=success("Auto-role updated", role.mention if role else "Disabled"), ephemeral=True)

    @app_commands.command(name="welcomedm", description="Enable or disable welcome DMs.")
    @app_commands.describe(enabled="Whether to DM new members")
    @administrator()
    async def welcomedm(self, interaction: discord.Interaction, enabled: bool) -> None:
        assert interaction.guild
        async with SessionLocal() as database:
            await update_config(database, interaction.guild.id, dm_welcome=enabled)
        await interaction.response.send_message(embed=success("Welcome DMs updated", "Enabled" if enabled else "Disabled"), ephemeral=True)

    async def send_join(self, member: discord.Member) -> None:
        async with SessionLocal() as database:
            config = await get_config(database, member.guild.id)
        text = render(config.welcome_message, member)
        if config.welcome_enabled and config.welcome_channel_id:
            channel = member.guild.get_channel(config.welcome_channel_id)
            if isinstance(channel, discord.TextChannel):
                try:
                    await channel.send(embed=embed("Welcome!", text) if config.welcome_embed else text)
                except discord.HTTPException:
                    pass
        if config.dm_welcome:
            try:
                await member.send(text)
            except discord.HTTPException:
                pass

    async def send_leave(self, member: discord.Member) -> None:
        async with SessionLocal() as database:
            config = await get_config(database, member.guild.id)
        if config.goodbye_enabled and config.goodbye_channel_id:
            channel = member.guild.get_channel(config.goodbye_channel_id)
            if isinstance(channel, discord.TextChannel):
                try:
                    await channel.send(embed=embed("Goodbye", render(config.goodbye_message, member)))
                except discord.HTTPException:
                    pass