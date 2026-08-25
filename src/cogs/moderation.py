import discord
from discord import app_commands
from discord.ext import commands
from sqlalchemy import desc, select

from src.database import SessionLocal
from src.models import ModerationCase, Warning
from src.services.moderation import add_warning, record_case, timeout_member
from src.utils.checks import hierarchy_safe, moderator
from src.utils.embeds import embed, error, success


class ModerationCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def _target_check(self, interaction: discord.Interaction, target: discord.Member) -> tuple[bool, str]:
        assert interaction.guild
        actor = interaction.user
        if not isinstance(actor, discord.Member):
            return False, "This command can only be used in a server."
        return hierarchy_safe(actor, target, interaction.guild.me)

    @app_commands.command(name="warn", description="Issue a warning and create a moderation case.")
    @app_commands.describe(member="Member to warn", reason="Reason for the warning")
    @moderator()
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str) -> None:
        ok, message = await self._target_check(interaction, member)
        if not ok:
            await interaction.response.send_message(message, ephemeral=True)
            return
        assert interaction.guild and isinstance(interaction.user, discord.Member)
        async with SessionLocal() as database:
            warning = await add_warning(database, interaction.guild, member, interaction.user, reason[:1000])
        try:
            await member.send(f"You were warned in **{interaction.guild.name}**: {reason[:1000]}")
        except discord.HTTPException:
            pass
        await interaction.response.send_message(embed=success("Warning issued", f"{member.mention} received warning case `#{warning.id}`."))

    @app_commands.command(name="timeout", description="Timeout a member for a number of minutes.")
    @app_commands.describe(member="Member to timeout", minutes="1–40320 minutes", reason="Reason")
    @moderator()
    async def timeout(self, interaction: discord.Interaction, member: discord.Member, minutes: app_commands.Range[int, 1, 40320], reason: str = "No reason provided") -> None:
        ok, message = await self._target_check(interaction, member)
        if not ok:
            await interaction.response.send_message(message, ephemeral=True)
            return
        assert interaction.guild and isinstance(interaction.user, discord.Member)
        try:
            await timeout_member(member, minutes, reason[:1000])
        except discord.Forbidden:
            await interaction.response.send_message(embed=error("Timeout failed", "Check my Moderate Members permission and role hierarchy."), ephemeral=True)
            return
        async with SessionLocal() as database:
            case = await record_case(database, interaction.guild, member.id, interaction.user.id, "timeout", reason[:1000])
        await interaction.response.send_message(embed=success("Member timed out", f"{member.mention} · case `#{case.id}`"))

    @app_commands.command(name="kick", description="Kick a member.")
    @app_commands.describe(member="Member to kick", reason="Reason")
    @moderator()
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided") -> None:
        ok, message = await self._target_check(interaction, member)
        if not ok:
            await interaction.response.send_message(message, ephemeral=True)
            return
        assert interaction.guild and isinstance(interaction.user, discord.Member)
        try:
            await member.kick(reason=reason[:1000])
        except discord.Forbidden:
            await interaction.response.send_message(embed=error("Kick failed", "Check my Kick Members permission and role hierarchy."), ephemeral=True)
            return
        async with SessionLocal() as database:
            case = await record_case(database, interaction.guild, member.id, interaction.user.id, "kick", reason[:1000])
        await interaction.response.send_message(embed=success("Member kicked", f"{member.mention} · case `#{case.id}`"))

    @app_commands.command(name="ban", description="Ban a member.")
    @app_commands.describe(member="Member to ban", reason="Reason")
    @moderator()
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided") -> None:
        ok, message = await self._target_check(interaction, member)
        if not ok:
            await interaction.response.send_message(message, ephemeral=True)
            return
        assert interaction.guild and isinstance(interaction.user, discord.Member)
        try:
            await member.ban(reason=reason[:1000], delete_message_seconds=0)
        except discord.Forbidden:
            await interaction.response.send_message(embed=error("Ban failed", "Check my Ban Members permission and role hierarchy."), ephemeral=True)
            return
        async with SessionLocal() as database:
            case = await record_case(database, interaction.guild, member.id, interaction.user.id, "ban", reason[:1000])
        await interaction.response.send_message(embed=success("Member banned", f"{member.mention} · case `#{case.id}`"))

    @app_commands.command(name="case", description="View a moderation case.")
    @app_commands.describe(case_id="Case number")
    @moderator()
    async def case(self, interaction: discord.Interaction, case_id: int) -> None:
        assert interaction.guild
        async with SessionLocal() as database:
            item = await database.get(ModerationCase, case_id)
        if not item or item.guild_id != interaction.guild.id:
            await interaction.response.send_message("That case does not exist in this server.", ephemeral=True)
            return
        await interaction.response.send_message(
            embed=embed(
                f"Case #{item.id} · {item.action.title()}",
                f"**Target:** <@{item.target_id}>\n**Moderator:** <@{item.moderator_id}>\n**Reason:** {item.reason}",
            ),
            ephemeral=True,
        )

    @app_commands.command(name="userinfo", description="Show useful information about a member.")
    @app_commands.describe(member="Member to inspect")
    async def userinfo(self, interaction: discord.Interaction, member: discord.Member | None = None) -> None:
        member = member or interaction.user
        assert isinstance(member, discord.Member)
        await interaction.response.send_message(
            embed=embed(
                f"User information · {member}",
                f"ID: `{member.id}`\nJoined: {discord.utils.format_dt(member.joined_at, 'R') if member.joined_at else 'unknown'}\n"
                f"Created: {discord.utils.format_dt(member.created_at, 'R')}\nRoles: {len(member.roles) - 1}",
            )
        )

    @app_commands.command(name="serverinfo", description="Show information about this server.")
    async def serverinfo(self, interaction: discord.Interaction) -> None:
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("This command is server-only.", ephemeral=True)
            return
        await interaction.response.send_message(
            embed=embed(
                f"Server information · {guild.name}",
                f"ID: `{guild.id}`\nOwner: <@{guild.owner_id}>\nMembers: `{guild.member_count}`\n"
                f"Channels: `{len(guild.channels)}`\nCreated: {discord.utils.format_dt(guild.created_at, 'R')}",
            )
        )