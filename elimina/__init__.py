import logging

import discord
from discord.ext import commands

from elimina.config import Config

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)

LOGGER.addHandler(handler)

LOGGER.propagate = False

LOGGER.info("Logger initialized.")

config = Config()

client = commands.Bot(
    command_prefix="~",
    intents=discord.Intents(53608189),  # default intents + message content
    status="Online",
    case_insensitive=True,
)

client.remove_command("timer")
client.remove_command("help")
