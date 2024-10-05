import logging

import discord

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
    intents=discord.Intents().all(),  # default intents + message content
    status="Online",
    case_insensitive=True,
    shards=32,
    help_command=None,
)
