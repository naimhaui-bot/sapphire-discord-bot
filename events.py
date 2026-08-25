import discord
from discord.ext import commands

from src.database import SessionLocal
from src.services.settings import top_custom_commands


class EventCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        welcome = self.bot.get_cog("WelcomeCog")
        protection = self.bot.get_cog("HoneypotCog")
        if welcome:
            await welcome.send_join(member)
        if protection:
            await protection.inspect_join(member)
        async with SessionLocal() as database:
            from src.services.settings import get_config
            config = await get_config(database, member.guild.id)
        if config.autorole_id and member.guild.me:
            role = member.guild.get_role(config.autorole_id)
            if role and role < member.guild.me.top_role:
                try:
                    await member.add_roles(role, reason="Sapphire auto-role")
                except discord.HTTPException:
                    pass

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member) -> None:
        welcome = self.bot.get_cog("WelcomeCog")
        if welcome:
            await welcome.send_leave(member)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot or not message.guild:
            return
        protection = self.bot.get_cog("HoneypotCog")
        if protection:
            await protection.inspect_message(message)
        leveling = self.bot.get_cog("LevelingCog")
        if leveling:
            await leveling.process_message(message)
        async with SessionLocal() as database:
            commands_map = await top_custom_commands(database, message.guild.id)
        name = message.content.strip().lower()
        if name in commands_map and isinstance(message.channel, discord.TextChannel):
            await message.channel.send(commands_map[name].replace("{mention}", message.author.mention))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(EventCog(bot))