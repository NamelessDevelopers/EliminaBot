import asyncio

from elimina import LOGGER, client, config


# load cogs
async def load_extensions() -> None:
    LOGGER.info("Loading extensions...")
    await client.load_extension("elimina.commands.admin")
    await client.load_extension("elimina.commands.info")
    await client.load_extension("elimina.commands.mod")
    await client.load_extension("elimina.commands.utility")
    await client.load_extension("elimina.handlers.error_handler")
    await client.load_extension("elimina.handlers.event_handler")


async def main():
    LOGGER.info("Starting Elimina...")
    await client.login(config.BOT_TOKEN)
    await load_extensions()
    await client.connect()


if __name__ == "__main__":
    asyncio.run(main())
