from elimina import LOGGER, client, config


def main():
    LOGGER.info("Starting Elimina...")
    client.run(config.BOT_TOKEN)


if __name__ == "__main__":
    main()
