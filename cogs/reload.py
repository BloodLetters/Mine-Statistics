import discord
from discord import app_commands

class Reload(app_commands.Command):
    def __init__(self, bot):
        super().__init__(
            name="reload",
            description="Reload all server statuses immediately",
            callback=self.reload_callback
        )
        self.bot = bot

    async def reload_callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        # Check if the user is a staff member
        if not self.bot.db.is_staff(str(interaction.user.id)):
            print(self.bot.db.is_staff(str(interaction.user.id)))
            await interaction.followup.send(
                "You don't have permission to use this command.",
                ephemeral=True
            )

            print(self.bot.db.is_staff(str(interaction.user.id)))
            return

        try:
            await self.bot.minecraft.update_all_servers(self.bot)
            await interaction.followup.send(
                "All server statuses have been reloaded!",
                ephemeral=True
            )
        except Exception as e:
            print(f"Error in reload command: {e}")
            await interaction.followup.send(
                "An error occurred while reloading server statuses.",
                ephemeral=True
            )