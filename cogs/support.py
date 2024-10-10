import discord

from discord import app_commands

class Support(app_commands.Command):
    def __init__(self, bot):
        super().__init__(
            name="support",
            description="Showing bot supports",
            callback=self.callback
        )
        self.bot = bot
        
    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Bot Statistics", color=discord.Color.green())
        embed.add_field(name="Information", value=f"If you getting any error pls contact us", inline=False)
        embed.add_field(name="Support", value=f"(Click here)[https://discord.gg/hZTy9TafAM]", inline=False)
        embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else self.bot.user.default_avatar.url)
        
        await interaction.response.send_message(embed=embed)