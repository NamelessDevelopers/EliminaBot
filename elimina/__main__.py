import asyncio

from elimina import LOGGER, client, config, load_extensions


async def main():
    LOGGER.info("Starting Elimina...")
    await client.login(config.BOT_TOKEN)
    await load_extensions(client)
    await client.connect()


if __name__ == "__main__":
    asyncio.run(main())
