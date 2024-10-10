import discord
import os

from discord.ext import tasks
from datetime import datetime

from cogs.register import Register
from cogs.unregister import Unregister
from cogs.reload import Reload
from cogs.help import Help
from cogs.stats import Stats

from utils.database import Database
from utils.minecraft import MinecraftServer

# Konfigurasi
DISCORD_TOKEN = os.environ['DISCORD_TOKEN']

class MinecraftMonitorBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = discord.app_commands.CommandTree(self)
        self.tree.remove_command('help')
        self.db = Database()
        self.minecraft = MinecraftServer()

    async def setup_hook(self):
        # Load all cogs
        self.tree.add_command(Register(self))
        self.tree.add_command(Unregister(self))
        self.tree.add_command(Reload(self))
        self.tree.add_command(Stats(self))
        self.tree.add_command(Help(self))
        await self.tree.sync()

    async def start_tasks(self):
        self.update_status.start()

    @tasks.loop(minutes=5)
    async def update_status(self):
        await self.minecraft.update_all_servers(self)

    @update_status.before_loop
    async def before_update_status(self):
        await self.wait_until_ready()

    async def on_ready(self):
        print(f'Bot logged in as {self.user}')
        await self.start_tasks()