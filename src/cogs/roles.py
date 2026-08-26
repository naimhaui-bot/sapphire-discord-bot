import discord
from discord import app_commands
from discord.ext import commands

from src.utils.checks import moderator
from src.utils.embeds import error, success


class RoleCog(commands.Cog):
    role = app_commands.Group(name="role", description="Manage member roles.")

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def _check(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        role: discord.Role,
    ) -> str | None:
        if not isinstance(interaction.user, discord.Member) or not interaction.guild:
            return "This command can only be used in a server."
        if role.is_default() or role.managed:
            return "That role cannot be managed."
        if role >= interaction.user.top_role and interaction.user != interaction.guild.owner:
            return "That role is equal to or higher than your highest role."
        if interaction.guild.me and role >= interaction.guild.me.top_role:
            return "That role is equal to or higher than my highest role."
        if member == interaction.user and not interaction.user.guild_permissions.administrator:
            return "You cannot change your own roles with this command."
        return None

    @role.command(name="add", description="Add a role to a member.")
    @app_commands.describe(member="Member", role="Role to add")
    @moderator()
    async def add(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        role: discord.Role,
    ) -> None:
        message = await self._check(interaction, member, role)
        if message:
            await interaction.response.send_message(
                embed=error("Role update blocked", message),
                ephemeral=True,
            )
            return
        try:
            await member.add_roles(role, reason=f"Role command by {interaction.user}")
        except discord.Forbidden:
            await interaction.response.send_message(
                embed=error("Role update failed", "I cannot manage that role."),
                ephemeral=True,
            )
            return
        await interaction.response.send_message(
            embed=success("Role added", f"{role.mention} was added to {member.mention}.")
        )

    @role.command(name="remove", description="Remove a role from a member.")
    @app_commands.describe(member="Member", role="Role to remove")
    @moderator()
    async def remove(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        role: discord.Role,
    ) -> None:
        message = await self._check(interaction, member, role)
        if message:
            await interaction.response.send_message(
                embed=error("Role update blocked", message),
                ephemeral=True,
            )
            return
        try:
            await member.remove_roles(role, reason=f"Role command by {interaction.user}")
        except discord.Forbidden:
            await interaction.response.send_message(
                embed=error("Role update failed", "I cannot manage that role."),
                ephemeral=True,
            )
            return
        await interaction.response.send_message(
            embed=success("Role removed", f"{role.mention} was removed from {member.mention}.")
        )