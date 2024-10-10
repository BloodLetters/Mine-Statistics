import discord
from discord import app_commands

class Register(app_commands.Command):
    def __init__(self, bot):
        super().__init__(
            name="register",
            description="Register a Minecraft server for monitoring",
            callback=self.register_callback
        )
        self.bot = bot

    async def register_callback(self, interaction: discord.Interaction, serverip: str, jenisserver: str):
        await interaction.response.defer(ephemeral=False)
        
        if jenisserver.lower() not in ['java', 'bedrock']:
            await interaction.followup.send(
                "Invalid server type. Please use 'java' or 'bedrock'.",
                ephemeral=True
            )
            return
        
        try:
            existing_server = self.bot.db.get_server(serverip)
            
            if existing_server.data:
                await interaction.followup.send(
                    "This server is already registered!",
                    ephemeral=True
                )
                return

            status = await self.bot.minecraft.get_server_status(serverip, jenisserver)
            if not status["online"]:
                await interaction.followup.send(
                    f"Unable to connect to the server. Please verify the IP and try again.\nError: {status.get('error', 'Unknown error')}",
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
                {"server_ip": serverip, "server_type": jenisserver},
                status
            )
            status_message = await channel.send(embed=embed)
            
            server_data = {
                'server_ip': serverip,
                'server_type': jenisserver.lower(),
                'registered_by': str(interaction.user.id),
                'channel_id': str(channel.id),
                'message_id': str(status_message.id)
            }
            
            self.bot.db.add_server(server_data)
            
            await interaction.followup.send(
                f"Server successfully registered and being monitored in {channel.mention}!",
                ephemeral=False
            )
            
        except Exception as e:
            print(f"Error in register command: {e}")
            await interaction.followup.send(
                "An error occurred during registration.",
                ephemeral=True
            )