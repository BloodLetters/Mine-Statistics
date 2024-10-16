import discord
import psutil
import platform
import time
import os

from datetime import datetime, timezone
from discord import app_commands

class Stats(app_commands.Command):
    def __init__(self, bot):
        super().__init__(
            name="stats",
            description="Showing bot stats",
            callback=self.callback
        )
        self.bot = bot
        
    async def callback(self, interaction: discord.Interaction):
        python_version = platform.python_version()
        discord_py_version = discord.__version__

        total_users = sum(guild.member_count for guild in self.bot.guilds)
        total_guilds = len(self.bot.guilds)
        total_staff = len(self.bot.db.staff_list())

        cpu_usage = psutil.cpu_percent()
        monitored_servers = len(self.bot.db.get_all_servers().data)

        embed = discord.Embed(title="Bot Information", color=discord.Color.green())
        embed.add_field(name="``⚙️ Discord.py``", value=f"```{discord_py_version}```", inline=True)
        embed.add_field(name="``🐍 Python``", value=f"```{python_version}```", inline=True)
        embed.add_field(name="``☁️ Uptime``", value=f"```{get_uptime(self.bot.uptime)}```")

        # embed.add_field(name="", value=f"", inline=True)
        embed.add_field(name="``📈 Total Users``", value=f"```{total_users} Users```", inline=True)
        embed.add_field(name="``📜 Total Server``", value=f"```{total_guilds} Server```", inline=True)
        embed.add_field(name="``🛡️ Total Staff``", value=f"```{total_staff} Staff```", inline=True)

        embed.add_field(name="``📟 RAM Usage``", value=f"```{get_memory_usage()}```", inline=True)
        embed.add_field(name="``⚡ CPU Usage``", value=f"```{cpu_usage}%```", inline=True)
        embed.add_field(name="``📂 Server Registered``", value=f"```{monitored_servers} Server```", inline=True)
        # embed.add_field(name="⚙️ System", value=f"CPU Usage: {cpu_usage}%\nRAM Usage: {ram_usage}%", inline=False)
        # embed.add_field(name="Versions", value=f"Python: {python_version}\ndiscord.py: {discord_py_version}", inline=False)
        # embed.add_field(name="Bot", value=f"Guilds Joined: {total_guilds}\nTotal Users: {total_users}", inline=False)
        # embed.add_field(name="Minecraft Servers", value=f"Monitored: {monitored_servers}", inline=False)
        # embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else self.bot.user.default_avatar.url)
        embed.timestamp = datetime.now(timezone.utc)
        await interaction.response.send_message(embed=embed)

def get_memory_usage():
    try:
        current_process = psutil.Process(os.getpid())
        memory_info = current_process.memory_info()
        memory_usage_mb = memory_info.rss / 1024 / 1024
        return f"{memory_usage_mb:.2f} MB"
    except Exception as e:
        print(f"Error: {str(e)}")
        return f"Error!"
        
def get_uptime(time_old):
    uptime_seconds = time.time() - time_old
    
    days = uptime_seconds // (24 * 3600)
    uptime_seconds = uptime_seconds % (24 * 3600)
    hours = uptime_seconds // 3600
    uptime_seconds %= 3600
    minutes = uptime_seconds // 60
    seconds = uptime_seconds % 60
    
    return f"{int(days)}:{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
