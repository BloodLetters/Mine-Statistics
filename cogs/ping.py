import discord
import re

from discord import app_commands

class Ping(app_commands.Command):
    def __init__(self, bot):
        super().__init__(
            name="ping",
            description="Ping server to showing status",
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
        
        isvalid = self.is_valid_address(address)
        if not isvalid['valid']:
            await interaction.followup.send(
                "Invalid server address. Please provide a valid IP address or domain name.",
                ephemeral=True
            )
            return
        
        try:
            status = await self.bot.minecraft.get_server_status(address, server_type.value, server_port)
            if not status["online"]:
                await interaction.followup.send(
                    f"Unable to connect to the server. Please verify the address and port, then try again.\nError: {status.get('error', 'Unknown error')}",
                    ephemeral=True
                )
                return
            
            embed = self.bot.minecraft.create_embed(
                {
                    "server_ip": address, 
                    "server_type": server_type.value, "server_port": server_port
                },
                status
            )

            await interaction.followup.send(embed=embed)
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
