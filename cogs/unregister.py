import discord
from discord import app_commands

class Unregister(app_commands.Command):
    def __init__(self, bot):
        super().__init__(
            name="unregister",
            description="Unregister the Minecraft server from monitoring",
            callback=self.callback
        )
        self.bot = bot

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
