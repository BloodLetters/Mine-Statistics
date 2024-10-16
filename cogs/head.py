import discord

from discord import app_commands

class Head(app_commands.Command):
    def __init__(self, bot):
        super().__init__(
            name="head",
            description="Get player head",
            callback=self.callback
        )
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        # TODO: Adding /head command
        return