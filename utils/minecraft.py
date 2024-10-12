import discord
import re
import asyncio

from mcstatus import JavaServer, BedrockServer
from datetime import datetime, timezone
from collections import deque

class MinecraftServer:
    def __init__(self, max_concurrent_requests=50, cache_ttl=300):
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)
        self.cache = {}
        self.cache_ttl = cache_ttl
        self.queue = deque()

    async def get_server_status(self, server_ip: str, server_type: str, server_port: int = None):
        async with self.semaphore:
            # Check cache first
            cache_key = f"{server_ip}:{server_port}:{server_type}"
            if cache_key in self.cache:
                cached_data, timestamp = self.cache[cache_key]
                if (datetime.now(timezone.utc) - timestamp).total_seconds() < self.cache_ttl:
                    return cached_data

            try:
                address = f"{server_ip}:{server_port}" if server_port else server_ip
                if server_type.lower() == "java":
                    server = JavaServer.lookup(address)
                    status = await server.async_status()
                    result = {
                        "online": True,
                        "players_online": status.players.online,
                        "players_max": status.players.max,
                        "motd": status.description,
                        "latency": round(status.latency, 2),
                        "version": status.version.name
                    }
                elif server_type.lower() == "bedrock":
                    server = BedrockServer.lookup(address)
                    status = await server.async_status()
                    result = {
                        "online": True,
                        "players_online": status.players_online,
                        "players_max": status.players_max,
                        "motd": status.motd,
                        "latency": round(status.latency, 2),
                        "version": status.version.version
                    }
                
                # Update cache
                self.cache[cache_key] = (result, datetime.now(timezone.utc))
                return result
            except Exception as e:
                print(f"Error checking server status: {e}")
                return {
                    "online": False,
                    "error": str(e)
                }

    def create_embed(self, server_data: dict, status_data: dict):
        if status_data["online"]:
            if status_data['version'] == "":
                status_data['version'] = "None"

            embed = discord.Embed(
                title="Minecraft Server Status",
                description="Server is ONLINE",
                color=discord.Color.green(),
                timestamp=datetime.now(timezone.utc)
            )
            
            server_info = f"**IP:** {server_data['server_ip']}\n"
            if server_data.get('server_port'):
                server_info += f"**Port:** {server_data['server_port']}\n"
            server_info += f"**Type:** {server_data['server_type'].upper()}\n"
            server_info += f"**Version:** {status_data['version']}"
            
            embed.add_field(
                name="Server Information",
                value=server_info,
                inline=False
            )
            
            embed.add_field(
                name="Players",
                value=f"**Online:** {status_data['players_online']}/{status_data['players_max']}",
                inline=True
            )
            
            embed.add_field(
                name="Latency",
                value=f"{status_data['latency']}ms",
                inline=True
            )
            
            motd = status_data['motd']
            if isinstance(motd, str):
                cleaned_motd = re.sub(r'§[0-9a-fk-or]', '', motd)
            else:
                cleaned_motd = str(motd)
                
            embed.add_field(
                name="MOTD",
                value=cleaned_motd,
                inline=False
            )
            
            embed.set_thumbnail(url=f"https://api.mcsrvstat.us/icon/{server_data['server_ip']}")
        else:
            embed = discord.Embed(
                title="Minecraft Server Status",
                description="Server is OFFLINE",
                color=discord.Color.red(),
                timestamp=datetime.now(timezone.utc)
            )
            embed.add_field(
                name="Error",
                value=status_data.get("error", "Unknown error"),
                inline=False
            )
        
        return embed

    async def process_queue(self, bot):
        while self.queue:
            server_data = self.queue.popleft()
            await self.update_server(bot, server_data)

    async def update_server(self, bot, server_data):
        try:
            channel = bot.get_channel(int(server_data['channel_id']))
            if not channel:
                print(f"Channel not found for server {server_data['server_ip']}. Deleting")
                bot.db.delete_server(server_data['server_ip'], server_data['guild_id'], server_data.get('server_port'))
                return

            detect = bot.db.get_Embed(int(server_data['guild_id']), int(server_data['channel_id']), int(server_data['message_id']))
            if not detect:
                print(f"Embed not found for server {server_data['server_ip']}. Deleting")
                bot.db.delete_server(server_data['server_ip'], server_data['guild_id'], server_data.get('server_port'))
                return

            try:
                message = await channel.fetch_message(int(server_data['message_id']))
            except discord.NotFound:
                print(f"Message not found for server {server_data['server_ip']}. Creating new message.")
                status = await self.get_server_status(
                    server_data['server_ip'],
                    server_data['server_type'],
                    server_data.get('server_port')
                )
                embed = self.create_embed(server_data, status)
                new_message = await channel.send(embed=embed)
                
                bot.db.update_server(server_data['server_ip'], {
                    'message_id': str(new_message.id)
                }, server_data.get('server_port'))
                return

            status = await self.get_server_status(
                server_data['server_ip'],
                server_data['server_type'],
                server_data.get('server_port')
            )
            embed = self.create_embed(server_data, status)
            await message.edit(embed=embed)
            
        except Exception as e:
            print(f"Error updating status for server {server_data['server_ip']}: {e}")


    async def update_all_servers(self, bot):
        try:
            chunk_size = 1000
            offset = 0
            
            while True:
                result = bot.db.get_all_servers_chunk(chunk_size, offset)
                if not result.data:
                    break

                for server_data in result.data:
                    self.queue.append(server_data)

                offset += chunk_size

            workers = [asyncio.create_task(self.process_queue(bot)) for _ in range(10)]
            await asyncio.gather(*workers)

        except Exception as e:
            print(f"Error in update_all_servers: {e}")