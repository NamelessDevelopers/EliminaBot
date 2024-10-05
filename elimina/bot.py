from discord.ext import commands


class Elimina(commands.AutoShardedBot):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.remove_command("timer")
