import asyncio

import discord
from discord import app_commands
from discord.ext import commands
from sqlalchemy import desc, select

from src.database import SessionLocal
from src.models import AkinatorStat
from src.services.akinator import Game
from src.utils.embeds import embed, success


class GameView(discord.ui.View):
    def __init__(self, cog: "AkinatorCog", interaction: discord.Interaction, game: Game) -> None:
        super().__init__(timeout=180)
        self.cog = cog
        self.owner_id = interaction.user.id
        self.game = game
        self.message: discord.Message | None = None
        for label, value, style in (
            ("Yes", "yes", discord.ButtonStyle.success),
            ("No", "no", discord.ButtonStyle.danger),
            ("Maybe", "maybe", discord.ButtonStyle.secondary),
        ):
            button = discord.ui.Button(label=label, style=style, custom_id=f"akinator:{value}")
            button.callback = self.answer
            self.add_item(button)
        cancel = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.secondary, custom_id="akinator:cancel")
        cancel.callback = self.cancel
        self.add_item(cancel)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message("This is another member's game.", ephemeral=True)
            return False
        return True

    async def answer(self, interaction: discord.Interaction) -> None:
        value = interaction.data["custom_id"].split(":")[1]
        self.game.answer({"yes": True, "no": False, "maybe": None}[value])
        if self.game.finished:
            await self.cog.finish_game(interaction, self.game, self)
            return
        await interaction.response.edit_message(embed=self.cog.question_embed(self.game), view=self)

    async def cancel(self, interaction: discord.Interaction) -> None:
        self.cog.games.pop(self.owner_id, None)
        self.stop()
        await interaction.response.edit_message(embed=embed("Akinator cancelled", "Start a new game with `/akinator`."), view=None)

    async def on_timeout(self) -> None:
        self.cog.games.pop(self.owner_id, None)
        if self.message:
            try:
                await self.message.edit(embed=embed("Akinator expired", "The game timed out after three minutes."), view=None)
            except discord.HTTPException:
                pass


class AkinatorCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.games: dict[int, Game] = {}

    def question_embed(self, game: Game) -> discord.Embed:
        return embed("Akinator", f"Question **{game.question_index + 1}/10**\n\n{game.question[0]}")

    @app_commands.command(name="akinator", description="Play an interactive character guessing game.")
    async def akinator(self, interaction: discord.Interaction) -> None:
        if not interaction.guild:
            await interaction.response.send_message("This game is server-only.", ephemeral=True)
            return
        if interaction.user.id in self.games:
            await interaction.response.send_message("You already have an active game.", ephemeral=True)
            return
        game = Game(interaction.user.id)
        self.games[interaction.user.id] = game
        view = GameView(self, interaction, game)
        await interaction.response.send_message(embed=self.question_embed(game), view=view)
        view.message = await interaction.original_response()

    async def finish_game(self, interaction: discord.Interaction, game: Game, view: GameView) -> None:
        view.stop()
        self.games.pop(game.user_id, None)
        character = game.guess
        async with SessionLocal() as database:
            stat = await database.get(AkinatorStat, (interaction.guild.id, game.user_id))
            if stat is None:
                stat = AkinatorStat(guild_id=interaction.guild.id, user_id=game.user_id)
                database.add(stat)
            stat.games += 1
            stat.losses += 1
            await database.commit()
        await interaction.response.edit_message(
            embed=embed("My guess", f"I think your character is **{character.name}**, {character.description}.\n\nWas I right? Use `/akinator` to play again."),
            view=None,
        )

    @app_commands.command(name="akinatorstats", description="Show Akinator game statistics.")
    async def akinatorstats(self, interaction: discord.Interaction) -> None:
        if not interaction.guild:
            await interaction.response.send_message("This command is server-only.", ephemeral=True)
            return
        async with SessionLocal() as database:
            stat = await database.get(AkinatorStat, (interaction.guild.id, interaction.user.id))
        if not stat:
            await interaction.response.send_message(embed=embed("Akinator statistics", "You have not played yet."))
            return
        await interaction.response.send_message(embed=embed("Akinator statistics", f"Games: `{stat.games}`\nWins: `{stat.wins}`\nLosses: `{stat.losses}`"))

    @app_commands.command(name="akinatorleaderboard", description="Show the Akinator leaderboard.")
    async def akinatorleaderboard(self, interaction: discord.Interaction) -> None:
        if not interaction.guild:
            await interaction.response.send_message("This command is server-only.", ephemeral=True)
            return
        async with SessionLocal() as database:
            result = await database.execute(select(AkinatorStat).where(AkinatorStat.guild_id == interaction.guild.id).order_by(desc(AkinatorStat.wins)).limit(10))
            stats = list(result.scalars())
        lines = [f"**{index}.** <@{stat.user_id}> · `{stat.wins}` wins / `{stat.games}` games" for index, stat in enumerate(stats, 1)]
        await interaction.response.send_message(embed=embed("Akinator leaderboard", "\n".join(lines) or "No games recorded yet."))