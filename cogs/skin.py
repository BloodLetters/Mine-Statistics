import discord

from discord import app_commands

class Skin(app_commands.Command):
    def __init__(self, bot):
        super().__init__(
            name="skin",
            description="Get player skin",
            callback=self.callback
        )
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        # TODO: Adding /skin command
        return