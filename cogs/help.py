import discord
from discord import app_commands

class Help(app_commands.Command):
    def __init__(self, bot):
        super().__init__(
            name="help",
            description="Showing bots help command",
            callback=self.callback
        )
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Bot Commands", color=discord.Color.blue())
        embed.add_field(name="/register", value="Register a Minecraft server for monitoring", inline=False)
        embed.add_field(name="/unregister", value="Unregister a Minecraft server from monitoring", inline=False)
        embed.add_field(name="/reload", value="Reload the server status manually", inline=False)
        embed.add_field(name="/stats", value="Show bot statistics", inline=False)
        embed.set_footer(text="Use /help [command] for more details on a specific command")
        
        await interaction.response.send_message(embed=embed)