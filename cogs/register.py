import discord
import re

from discord import app_commands
from datetime import datetime, timezone

class Register(app_commands.Command):
    def __init__(self, bot):
        super().__init__(
            name="register",
            description="Register a Minecraft server for monitoring",
            callback=self.callback
        )
        self.bot = bot

    @app_commands.describe(
        address="The IP address of the Minecraft server",
        server_type="The type of Minecraft server (Java or Bedrock)",
        server_port="The port of the Minecraft server (optional)"
    )
    @app_commands.choices(server_type=[
        app_commands.Choice(name="Java", value="java"),
        app_commands.Choice(name="Bedrock", value="bedrock")
    ])
    async def callback(self, interaction: discord.Interaction, address: str, server_type: app_commands.Choice[str], server_port: int = None):
        await interaction.response.defer(ephemeral=False)
        bot_member = interaction.guild.me

        if bot_member.guild_permissions.manage_channels == False:
            await interaction.send("I Dont have manage channel permission. give it to me first")
            return
            
        if not (interaction.user.id == interaction.guild.owner_id or 
                interaction.user.guild_permissions.administrator):
            await interaction.followup.send(
                "You don't have permission to use this command. Only the server owner or administrators can register servers.",
                ephemeral=True
            )
            return
        
        isvalid = self.is_valid_address(address)
        if not isvalid['valid']:
            await interaction.followup.send(
                "Invalid server address. Please provide a valid IP address or domain name.",
                ephemeral=True
            )
            return

        try:
            existing_server = self.bot.db.get_server_by_guild(str(interaction.guild.id))
            
            if existing_server.data and len(existing_server.data) > 0:
                await interaction.followup.send(
                    "Your guild already has a registered Minecraft server. Please unregister it first before adding a new one.",
                    ephemeral=True
                )
                return

            status = await self.bot.minecraft.get_server_status(address, server_type.value, server_port)
            if not status["online"]:
                await interaction.followup.send(
                    f"Unable to connect to the server. Please verify the address and port, then try again.\nError: {status.get('error', 'Unknown error')}",
                    ephemeral=True
                )
                return
            
            channel = discord.utils.get(interaction.guild.channels, name='minecraft-status')
            if not channel:
                overwrites = {
                    interaction.guild.default_role: discord.PermissionOverwrite(send_messages=False),
                    interaction.guild.me: discord.PermissionOverwrite(send_messages=True)
                }
                channel = await interaction.guild.create_text_channel('minecraft-status', overwrites=overwrites)
            
            embed = self.bot.minecraft.create_embed(
                {"server_ip": address, "server_type": server_type.value, "server_port": server_port},
                status
            )
            status_message = await channel.send(embed=embed)
            
            server_data = {
                'server_ip': address,
                'server_type': server_type.value,
                'server_port': server_port,
                'registered_by': str(interaction.user.id),
                'channel_id': str(channel.id),
                'message_id': str(status_message.id),
                'guild_id': str(interaction.guild.id),
                'last_updated': datetime.now(timezone.utc).isoformat(),
                'update_interval': 300  # 5 minutes in seconds
            }
            
            self.bot.db.add_server(server_data)
            await interaction.followup.send(
                f"Server successfully registered and being monitored in {channel.mention}! The status will be updated periodically.",
                ephemeral=False
            )
            
        except Exception as e:
            print(f"Error in register command: {e}")
            await interaction.followup.send(
                "An error occurred during registration.",
                ephemeral=True
            )

    def is_valid_address(self, address):
        domain_pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
        ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        sql_injection_pattern = r'(\b(SELECT|INSERT|UPDATE|DELETE|FROM|WHERE|DROP|UNION|TABLE|OR|AND)\b)|(-{2}|;|\/\*|\*\/|@|@@|char|nchar|varchar|nvarchar|alter|begin|cast|create|cursor|declare|exec|execute|fetch|kill|open|sys|xp_)'

        if re.match(domain_pattern, address):
            return {'valid': True, 'type': 'domain'}
        
        elif re.match(ip_pattern, address):
            octets = address.split('.')
            if all(0 <= int(octet) <= 255 for octet in octets):
                return {'valid': True, 'type': 'ip'}
        
        if re.search(sql_injection_pattern, address, re.IGNORECASE):
            return {'valid': False, 'type': 'invalid'}

        return {'valid': False, 'type': 'invalid'}
