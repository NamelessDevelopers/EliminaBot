import logging

import discord
from discord.ext import commands

from elimina.bot import Elimina
from elimina.config import Config

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = discord.utils._ColourFormatter()
handler.setFormatter(formatter)

LOGGER.addHandler(handler)

LOGGER.propagate = False

LOGGER.info("Logger initialized.")

config = Config()

client = Elimina(
    command_prefix=config.BOT_PREFIX,
    intents=discord.Intents(53608189),  # default intents + message content
    status="Online",
    case_insensitive=True,
    shards=32,
    help_command=None,
)


# load cogs
async def load_extensions(client: commands.Bot) -> None:
    LOGGER.info("Loading extensions...")
    await client.load_extension("elimina.commands.admin")
    await client.load_extension("elimina.commands.info")
    await client.load_extension("elimina.commands.mod")
    await client.load_extension("elimina.commands.utility")
    await client.load_extension("elimina.commands.owner")
    await client.load_extension("elimina.handlers.error_handler")
    await client.load_extension("elimina.handlers.event_handler")
