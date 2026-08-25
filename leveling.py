import discord
from discord import app_commands
from discord.ext import commands

from src.database import SessionLocal
from src.services.leveling import award_message, get_user, leaderboard, level_for_xp, xp_required
from src.services.settings import get_config, update_config
from src.utils.checks import administrator, moderator
from src.utils.embeds import embed, success


class LevelingCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="rank", description="Show a member's Arcane level and XP.")
    @app_commands.describe(member="Member to inspect")
    async def rank(self, interaction: discord.Interaction, member: discord.Member | None = None) -> None:
        member = member or interaction.user
        assert interaction.guild and isinstance(member, discord.Member)
        async with SessionLocal() as database:
            user = await get_user(database, interaction.guild.id, member.id)
        needed = xp_required(user.level)
        await interaction.response.send_message(
            embed=embed(f"Arcane rank · {member.display_name}", f"Level **{user.level}**\nXP **{user.xp:,} / {needed:,}**\nMessages: `{user.messages:,}`")
        )

    @app_commands.command(name="leaderboard", description="Show the server XP leaderboard.")
    async def leaderboard_command(self, interaction: discord.Interaction) -> None:
        assert interaction.guild
        async with SessionLocal() as database:
            users = await leaderboard(database, interaction.guild.id)
        if not users:
            await interaction.response.send_message(embed=embed("Arcane leaderboard", "No XP has been earned yet."))
            return
        lines = [f"**{index}.** <@{user.user_id}> · level `{user.level}` · `{user.xp:,}` XP" for index, user in enumerate(users, 1)]
        await interaction.response.send_message(embed=embed("Arcane leaderboard", "\n".join(lines)))

    @app_commands.command(name="levels", description="Show the XP system configuration.")
    async def levels(self, interaction: discord.Interaction) -> None:
        assert interaction.guild
        async with SessionLocal() as database:
            config = await get_config(database, interaction.guild.id)
        await interaction.response.send_message(embed=embed("Arcane levels", f"XP rate: `{config.xp_rate:g}x`\nMessage cooldown: `{config.xp_cooldown}s`\nLevel-up channel: {f'<#{config.levelup_channel_id}>' if config.levelup_channel_id else 'current channel'}"))

    @app_commands.command(name="setlevel", description="Configure XP rate and cooldown.")
    @app_commands.describe(rate="XP multiplier from 0.1 to 10", cooldown="Seconds between XP awards")
    @administrator()
    async def setlevel(self, interaction: discord.Interaction, rate: app_commands.Range[float, 0.1, 10.0], cooldown: app_commands.Range[int, 5, 3600]) -> None:
        assert interaction.guild
        async with SessionLocal() as database:
            await update_config(database, interaction.guild.id, xp_rate=rate, xp_cooldown=cooldown)
        await interaction.response.send_message(embed=success("Arcane settings updated", f"Rate: `{rate:g}x` · cooldown: `{cooldown}s`"), ephemeral=True)

    @app_commands.command(name="addxp", description="Add XP to a member.")
    @app_commands.describe(member="Member", amount="XP amount")
    @moderator()
    async def addxp(self, interaction: discord.Interaction, member: discord.Member, amount: app_commands.Range[int, 1, 1000000]) -> None:
        assert interaction.guild
        async with SessionLocal() as database:
            user = await get_user(database, interaction.guild.id, member.id)
            user.xp += amount
            user.level = level_for_xp(user.xp)
            await database.commit()
        await interaction.response.send_message(embed=success("XP added", f"{member.mention} now has `{user.xp:,}` XP."))

    @app_commands.command(name="removexp", description="Remove XP from a member.")
    @app_commands.describe(member="Member", amount="XP amount")
    @moderator()
    async def removexp(self, interaction: discord.Interaction, member: discord.Member, amount: app_commands.Range[int, 1, 1000000]) -> None:
        assert interaction.guild
        async with SessionLocal() as database:
            user = await get_user(database, interaction.guild.id, member.id)
            user.xp = max(0, user.xp - amount)
            user.level = level_for_xp(user.xp)
            await database.commit()
        await interaction.response.send_message(embed=success("XP removed", f"{member.mention} now has `{user.xp:,}` XP."))

    async def process_message(self, message: discord.Message) -> None:
        if not message.guild or message.author.bot or not isinstance(message.author, discord.Member):
            return
        async with SessionLocal() as database:
            result = await award_message(database, message.author)
            if not result:
                return
            user, levelled, level = result
            if levelled:
                config = await get_config(database, message.guild.id)
        if levelled:
            channel = message.guild.get_channel(config.levelup_channel_id) if config.levelup_channel_id else message.channel
            if isinstance(channel, discord.TextChannel):
                text = config.levelup_message.replace("{mention}", message.author.mention).replace("{level}", str(level))
                try:
                    await channel.send(embed=success("Level up!", text))
                except discord.HTTPException:
                    pass