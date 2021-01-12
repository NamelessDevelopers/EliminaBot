import discord

from discord.ext import commands

from bot.utils.fileHandler import fileHandler, DATA, BOT


# Initialize the Bot client.
client = commands.Bot(command_prefix="~", status="Online", case_insensitive=True)
client.remove_command('help')
client.remove_command('timer')

def main():
    fileHandler()
    print("Done reading data:")
    print(DATA)
    print("Done reading bot:")
    print(BOT)

if __name__ == "__main__":
    main()

    # Loads Cogs.
    client.load_extension("bot.commands.administration")
    client.load_extension("bot.commands.info")
    client.load_extension("bot.commands.moderation")
    client.load_extension("bot.commands.utility")
    client.load_extension("bot.utils.eventHandler")
    client.load_extension("bot.utils.fileHandler")
    client.load_extension("bot.utils.errorHandler")

client.run("TOKEN")