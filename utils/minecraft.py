from mcstatus import JavaServer, BedrockServer
import discord

from datetime import datetime, timezone
import re

class MinecraftServer:
    async def get_server_status(self, server_ip: str, server_type: str):
        try:
            if server_type.lower() == "java":
                server = JavaServer.lookup(server_ip)
                status = await server.async_status()
                return {
                    "online": True,
                    "players_online": status.players.online,
                    "players_max": status.players.max,
                    "motd": status.description,
                    "latency": round(status.latency, 2),
                    "version": status.version.name
                }
            elif server_type.lower() == "bedrock":
                server = BedrockServer.lookup(server_ip)
                status = await server.async_status()
                return {
                    "online": True,
                    "players_online": status.players_online,
                    "players_max": status.players_max,
                    "motd": status.motd,
                    "latency": round(status.latency, 2),
                    "version": status.version.version
                }
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
            
            embed.add_field(
                name="Server Information",
                value=f"**IP:** {server_data['server_ip']}\n"
                      f"**Type:** {server_data['server_type'].upper()}\n"
                      f"**Version:** {status_data['version']}",
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

    async def update_all_servers(self, bot):
        try:
            result = bot.db.get_all_servers()
            if not result.data:
                return

            for server_data in result.data:
                try:
                    channel = bot.get_channel(int(server_data['channel_id']))
                    if not channel:
                        print(f"Channel not found for server {server_data['server_ip']}. Deleting")
                        bot.db.delete_server(server_data['server_ip'], server_data['guild_id'])
                        continue
                    
                    detect = bot.db.get_Embed(int(server_data['guild_id']), int(server_data['channel_id']), int(server_data['message_id']))
                    if not detect:
                        print(f"Embed not found for server {server_data['server_ip']}. Deleting")
                        bot.db.delete_server(server_data['server_ip'], server_data['guild_id'])
                        continue
                    
                    try:
                        message = await channel.fetch_message(int(server_data['message_id']))
                    except discord.NotFound:
                        print(f"Message not found for server {server_data['server_ip']}. Creating new message.")
                        status = await self.get_server_status(
                            server_data['server_ip'],
                            server_data['server_type']
                        )
                        embed = self.create_embed(server_data, status)
                        new_message = await channel.send(embed=embed)
                        
                        bot.db.update_server(server_data['server_ip'], {
                            'message_id': str(new_message.id)
                        })
                        continue
                    
                    status = await self.get_server_status(
                        server_data['server_ip'],
                        server_data['server_type']
                    )
                    embed = self.create_embed(server_data, status)
                    await message.edit(embed=embed)
                    
                except Exception as e:
                    print(f"Error updating status for server {server_data['server_ip']}: {e}")
                    continue

        except Exception as e:
            print(f"Error in update_all_servers: {e}")