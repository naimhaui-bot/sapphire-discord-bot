import discord

COLOUR = discord.Colour(0x5865F2)
SUCCESS = discord.Colour(0x57F287)
WARNING = discord.Colour(0xFEE75C)
DANGER = discord.Colour(0xED4245)


def embed(title: str, description: str = "", colour: discord.Colour = COLOUR) -> discord.Embed:
    return discord.Embed(title=title, description=description, colour=colour)


def success(title: str, description: str = "") -> discord.Embed:
    return embed(title, description, SUCCESS)


def error(title: str, description: str = "") -> discord.Embed:
    return embed(title, description, DANGER)


def warning(title: str, description: str = "") -> discord.Embed:
    return embed(title, description, WARNING)