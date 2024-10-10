import discord
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
        server_type="The type of Minecraft server (Java or Bedrock)"
    )
    @app_commands.choices(server_type=[
        app_commands.Choice(name="Java", value="java"),
        app_commands.Choice(name="Bedrock", value="bedrock")
    ])
    async def callback(self, interaction: discord.Interaction, address: str, server_type: app_commands.Choice[str]):
        await interaction.response.defer(ephemeral=False)
        
        if not (interaction.user.id == interaction.guild.owner_id or 
                interaction.user.guild_permissions.administrator):
            await interaction.followup.send(
                "You don't have permission to use this command. Only the server owner or administrators can register servers.",
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

            status = await self.bot.minecraft.get_server_status(address, server_type.value)
            if not status["online"]:
                await interaction.followup.send(
                    f"Unable to connect to the server. Please verify the address and try again.\nError: {status.get('error', 'Unknown error')}",
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
                {"server_ip": address, "server_type": server_type.value},
                status
            )
            status_message = await channel.send(embed=embed)
            
            server_data = {
                'server_ip': address,
                'server_type': server_type.value,
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