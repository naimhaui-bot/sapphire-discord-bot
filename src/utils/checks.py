import discord
from discord import app_commands


def administrator() -> app_commands.Check:
    return app_commands.checks.has_permissions(administrator=True)


def moderator() -> app_commands.Check:
    async def predicate(interaction: discord.Interaction) -> bool:
        member = interaction.user
        return isinstance(member, discord.Member) and (
            member.guild_permissions.manage_messages
            or member.guild_permissions.moderate_members
            or member.guild_permissions.kick_members
            or member.guild_permissions.ban_members
            or member.guild_permissions.administrator
        )
    return app_commands.check(predicate)


def hierarchy_safe(
    actor: discord.Member, target: discord.Member, bot_member: discord.Member | None
) -> tuple[bool, str]:
    if target.id == actor.id:
        return False, "You cannot moderate yourself."
    if target == target.guild.owner:
        return False, "The server owner cannot be moderated."
    if target.top_role >= actor.top_role and actor != target.guild.owner:
        return False, "That member has an equal or higher role than you."
    if bot_member and target.top_role >= bot_member.top_role:
        return False, "That member's highest role is above my highest role."
    return True, ""