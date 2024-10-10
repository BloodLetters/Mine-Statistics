import discord
from discord import app_commands
import psutil
import platform

class Stats(app_commands.Command):
    def __init__(self, bot):
        super().__init__(
            name="stats",
            description="Showing bot stats",
            callback=self.callback
        )
        self.bot = bot
        
    async def callback(self, interaction: discord.Interaction):
        # Get system stats
        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.virtual_memory().percent
        python_version = platform.python_version()
        discord_py_version = discord.__version__

        # Get bot stats
        total_guilds = len(self.bot.guilds)
        total_users = sum(guild.member_count for guild in self.bot.guilds)

        # Get monitored servers count
        monitored_servers = len(self.bot.db.get_all_servers().data)

        embed = discord.Embed(title="Bot Statistics", color=discord.Color.green())
        embed.add_field(name="System", value=f"CPU Usage: {cpu_usage}%\nRAM Usage: {ram_usage}%", inline=False)
        embed.add_field(name="Versions", value=f"Python: {python_version}\ndiscord.py: {discord_py_version}", inline=False)
        embed.add_field(name="Bot", value=f"Guilds Joined: {total_guilds}\nTotal Users: {total_users}", inline=False)
        embed.add_field(name="Minecraft Servers", value=f"Monitored: {monitored_servers}", inline=False)

        await interaction.response.send_message(embed=embed)