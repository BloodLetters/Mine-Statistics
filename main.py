import discord
import os
import importlib
import time

from discord.ext import tasks

from cogs.ping import Ping
from cogs.register import Register
from cogs.unregister import Unregister
from cogs.reload import Reload
from cogs.help import Help
from cogs.stats import Stats
from cogs.support import Support

from utils.database import Database
from utils.minecraft import MinecraftServer

if os.getenv('DISCORD_TOKEN_BETA') != None:
    DISCORD_TOKEN = os.environ['DISCORD_TOKEN_BETA']
else:
    DISCORD_TOKEN = os.environ['DISCORD_TOKEN']

start_time = time.time()

class MinecraftMonitorBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = discord.app_commands.CommandTree(self)
        self.tree.remove_command("help")
        self.db = Database()
        self.uptime = start_time
        self.minecraft = MinecraftServer()
        self.cogs = [Register, Unregister, Reload, Stats, Support, Help, Ping]

    async def setup_hook(self):
        await self.load_cogs()
        await self.sync_commands()

    async def load_cogs(self):
        for cog in self.cogs:
            self.tree.add_command(cog(self))

    async def sync_commands(self):
        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(f"Failed to sync commands: {e}")

    async def reload_cogs(self):
        self.tree.clear_commands(guild=None)
        for cog in self.cogs:
            module = importlib.import_module(cog.__module__)
            importlib.reload(module)
        await self.load_cogs()
        await self.sync_commands()

    async def start_tasks(self):
        self.update_status.start()

    @tasks.loop(minutes=1)
    async def update_status(self):
        await self.minecraft.update_all_servers(self)

    @update_status.before_loop
    async def before_update_status(self):
        await self.wait_until_ready()

    async def on_ready(self):
        await self.sync_commands()
        await self.start_tasks()
        print(f'Bot logged in as {self.user}')