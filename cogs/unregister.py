import discord
import re

from discord import app_commands

class Unregister(app_commands.Command):
    def __init__(self, bot):
        super().__init__(
            name="unregister",
            description="Unregister the Minecraft server from monitoring",
            callback=self.callback
        )
        self.bot = bot

    @app_commands.describe(
        server_id="Server Address",
    )
    async def callback(self, interaction: discord.Interaction, server_id: str):
        await interaction.response.defer(ephemeral=True)

        if not (interaction.user.id == interaction.guild.owner_id or 
                interaction.user.guild_permissions.administrator):
            await interaction.followup.send(
                "You don't have permission to use this command. Only the server owner or administrators can unregister servers.",
                ephemeral=True
            )
            return
        
        try:
            server = self.bot.db.delete_server(server_id, str(interaction.guild.id))
            
            if not server.data:
                await interaction.followup.send(
                    "There is no Minecraft server registered with this ID for this Discord server!",
                    ephemeral=True
                )
                return
            
            server_data = server.data[0]
            
            try:
                channel = self.bot.get_channel(int(server_data['channel_id']))
                if channel:
                    message = await channel.fetch_message(int(server_data['message_id']))
                    if message:
                        await message.delete()
                        
            except Exception as e:
                print(f"Error deleting message: {e}")

            await interaction.followup.send(
                f"The Minecraft server with ID {server_id} has been unregistered from monitoring.",
                ephemeral=True
            )
            
        except Exception as e:
            print(f"Error in unregister command: {e}")
            await interaction.followup.send(
                "An error occurred while unregistering the server.",
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