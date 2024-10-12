import discord

from datetime import datetime, timezone
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
        embed.add_field(name="``⚙️ /register``", value="``Setup MC server``", inline=True)
        embed.add_field(name="``🗑️ /unregister``", value="``Delete MC server``", inline=True)
        embed.add_field(name="``🔄 /reload``", value="``Staff stuff only``", inline=True)
        embed.add_field(name="``📊 /stats``", value="``Show bot statistics``", inline=True)
        embed.add_field(name="``📶 /ping``", value="``Ping MC server``", inline=True)
        embed.add_field(name="``🎧 /support``", value="``Bot support server``", inline=True)
        embed.add_field(name=" ", value=" ")
        embed.add_field(name="``✈️ Usage``", value="``to use make sure use '/' command. example: /Setup, /Stats``", inline=False)
        embed.timestamp = datetime.now(timezone.utc)
        #embed.set_footer(text="Use /help for more details on a specific command")
        #embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else self.bot.user.default_avatar.url)
        
        await interaction.response.send_message(embed=embed)