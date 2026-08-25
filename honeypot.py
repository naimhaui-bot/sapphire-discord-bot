import discord
from discord import app_commands
from discord.ext import commands

from src.database import SessionLocal
from src.services.protection import is_staff_or_whitelisted, punish, register_join
from src.services.settings import get_config, update_config
from src.utils.checks import administrator
from src.utils.embeds import success, warning


class HoneypotCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="honeypot", description="Set a channel that silently detects suspicious messages.")
    @app_commands.describe(channel="Honeypot channel; omit to disable", punishment="timeout, kick, or ban")
    @administrator()
    async def honeypot(self, interaction: discord.Interaction, channel: discord.TextChannel | None = None, punishment: str = "timeout") -> None:
        if punishment not in {"timeout", "kick", "ban"}:
            await interaction.response.send_message("Punishment must be `timeout`, `kick`, or `ban`.", ephemeral=True)
            return
        assert interaction.guild
        async with SessionLocal() as database:
            await update_config(database, interaction.guild.id, honeypot_channel_id=channel.id if channel else None, honeypot_punishment=punishment)
        await interaction.response.send_message(embed=success("Honeypot updated", f"Channel: {channel.mention if channel else 'disabled'} · punishment: `{punishment}`"), ephemeral=True)

    @app_commands.command(name="raid", description="Configure join-rate anti-raid protection.")
    @app_commands.describe(threshold="Joins required", window="Window in seconds", action="timeout, kick, or ban")
    @administrator()
    async def raid(self, interaction: discord.Interaction, threshold: app_commands.Range[int, 2, 100], window: app_commands.Range[int, 5, 300], action: str = "timeout") -> None:
        if action not in {"timeout", "kick", "ban"}:
            await interaction.response.send_message("Action must be `timeout`, `kick`, or `ban`.", ephemeral=True)
            return
        assert interaction.guild
        async with SessionLocal() as database:
            await update_config(database, interaction.guild.id, raid_threshold=threshold, raid_window=window, raid_action=action)
        await interaction.response.send_message(embed=success("Raid protection updated", f"`{threshold}` joins / `{window}s` · `{action}`"), ephemeral=True)

    @app_commands.command(name="whitelist", description="Add or remove a protected member from anti-raid actions.")
    @app_commands.describe(member="Member", remove="Remove instead of add")
    @administrator()
    async def whitelist(self, interaction: discord.Interaction, member: discord.Member, remove: bool = False) -> None:
        assert interaction.guild
        async with SessionLocal() as database:
            config = await get_config(database, interaction.guild.id)
            ids = set(config.whitelist or [])
            if remove:
                ids.discard(member.id)
            else:
                ids.add(member.id)
            await update_config(database, interaction.guild.id, whitelist=list(ids))
        await interaction.response.send_message(embed=success("Whitelist updated", f"{member.mention} {'removed from' if remove else 'added to'} the whitelist."), ephemeral=True)

    @app_commands.command(name="lockdown", description="Enable or disable emergency lockdown.")
    @app_commands.describe(enabled="Whether new joins should be blocked")
    @administrator()
    async def lockdown(self, interaction: discord.Interaction, enabled: bool) -> None:
        assert interaction.guild
        async with SessionLocal() as database:
            await update_config(database, interaction.guild.id, emergency_lockdown=enabled)
        await interaction.response.send_message(embed=warning("Emergency lockdown", "Enabled" if enabled else "Disabled"), ephemeral=True)

    async def inspect_message(self, message: discord.Message) -> None:
        if not message.guild or not isinstance(message.author, discord.Member):
            return
        async with SessionLocal() as database:
            config = await get_config(database, message.guild.id)
            if config.honeypot_channel_id != message.channel.id:
                return
            if await is_staff_or_whitelisted(database, message.author):
                return
            punished = await punish(database, message.author, config.honeypot_punishment, "Sapphire honeypot triggered")
        if punished:
            try:
                await message.delete()
            except discord.HTTPException:
                pass

    async def inspect_join(self, member: discord.Member) -> None:
        async with SessionLocal() as database:
            config = await get_config(database, member.guild.id)
            raid = await register_join(database, member)
            if config.emergency_lockdown or raid:
                await punish(database, member, config.raid_action, "Sapphire anti-raid protection")