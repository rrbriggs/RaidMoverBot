import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import sqlite3
import os
import logging

load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

logging.basicConfig(
    level = logging.INFO,
    format='%(asctime)s:%(levelname)s:%(name)s: %(message)s'
)

# Intents required for the bot
intents = discord.Intents.default()
intents.members = True
intents.voice_states = True

class RaidMoverBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.db = sqlite3.connect('settings.db')
        self.cursor = self.db.cursor()
        self.setup_database()

    async def setup_hook(self):
        # Sync commands for each guild
        for guild in self.guilds:
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)

    def setup_database(self):
        # Create a table to store settings
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                guild_id INTEGER PRIMARY KEY,
                admin_role_id INTEGER DEFAULT NULL,
                raid_channel_id INTEGER DEFAULT NULL,
                destination_channel_id INTEGER DEFAULT NULL
            )
        ''')
        self.db.commit()

client = RaidMoverBot()

def is_admin(interaction: discord.Interaction):
    guild_id = interaction.guild.id
    user_roles = interaction.user.roles
    client.cursor.execute('SELECT admin_role_id FROM settings WHERE guild_id = ?', (guild_id,))
    result = client.cursor.fetchone()
    if result and result[0]:
        admin_role = interaction.guild.get_role(result[0])
        return admin_role in user_roles
    else:
        return interaction.user.guild_permissions.administrator

def admin_only():
    async def predicate(interaction: discord.Interaction):
        return is_admin(interaction)
    return app_commands.check(predicate)

@client.event
async def on_ready():
    logging.info(f'Logged in as {client.user}')

@client.event
async def on_guild_join(guild):
    client.tree.copy_global_to(guild=guild)
    await client.tree.sync(guild=guild)

@client.tree.command(name="setadminrole", description="Set the admin role for bot commands.")
@app_commands.checks.has_permissions(administrator=True)
async def set_admin_role(interaction: discord.Interaction, role: discord.Role):
    logging.info("Setting admin role")
    guild_id = interaction.guild.id
    client.cursor.execute('''
        INSERT INTO settings (guild_id, admin_role_id)
        VALUES (?, ?)
        ON CONFLICT(guild_id) DO UPDATE SET admin_role_id=excluded.admin_role_id
    ''', (guild_id, role.id))
    client.db.commit()
    await interaction.response.send_message(f"Admin role set to {role.name}", ephemeral=True)
    logging.info(f"Admin role set to '{role.name}' in guild '{interaction.guild.name}' by user '{interaction.user}'")

@client.tree.command(name="setraidchannel", description="Set the raid voice channel.")
@admin_only()
async def set_raid_channel(interaction: discord.Interaction, channel: discord.VoiceChannel):
    logging.info("Setting raid channel")
    guild_id = interaction.guild.id
    client.cursor.execute('''
        INSERT INTO settings (guild_id, raid_channel_id)
        VALUES (?, ?)
        ON CONFLICT(guild_id) DO UPDATE SET raid_channel_id=excluded.raid_channel_id
    ''', (guild_id, channel.id))
    client.db.commit()
    await interaction.response.send_message(f"Raid channel set to {channel.name}", ephemeral=True)
    logging.info(f"Raid channel set to '{channel.name}' in guild '{interaction.guild.name}' by user '{interaction.user}'")

@client.tree.command(name="setdestinationchannel", description="Set the destination voice channel.")
@admin_only()
async def set_destination_channel(interaction: discord.Interaction, channel: discord.VoiceChannel):
    logging.info("Setting destination channel")
    guild_id = interaction.guild.id
    client.cursor.execute('''
        INSERT INTO settings (guild_id, destination_channel_id)
        VALUES (?, ?)
        ON CONFLICT(guild_id) DO UPDATE SET destination_channel_id=excluded.destination_channel_id
    ''', (guild_id, channel.id))
    client.db.commit()
    await interaction.response.send_message(f"Destination channel set to {channel.name}", ephemeral=True)
    logging.info(f"Destination channel set to '{channel.name}' in guild '{interaction.guild.name}' by user '{interaction.user}'")

@client.tree.command(name="moveraid", description="Move users from the raid channel to the destination channel.")
@admin_only()
async def move_raid(interaction: discord.Interaction):
    logging.info("Moving the raid now")
    guild_id = interaction.guild.id
    client.cursor.execute('SELECT raid_channel_id, destination_channel_id FROM settings WHERE guild_id = ?', (guild_id,))
    result = client.cursor.fetchone()
    logging.info(f"Database query result: {result}")
    if result and result[0] and result[1]:
        raid_channel = interaction.guild.get_channel(result[0])
        destination_channel = interaction.guild.get_channel(result[1])
        logging.info(f"Raid Channel: {raid_channel}, Destination Channel: {destination_channel}")
        if raid_channel and destination_channel:
            members = raid_channel.members
            if members:
                await interaction.response.send_message(f"Moving {len(members)} members...", ephemeral=True)
                logging.info(f"Moving {len(members)} members from '{raid_channel.name}' to '{destination_channel.name}'")
                for member in members:
                    try:
                        await member.move_to(destination_channel)
                        logging.info(f"Moved member '{member.display_name}'")
                    except Exception as e:
                        logging.error(f"Could not move {member.display_name}: {e}")
                await interaction.followup.send("All members moved successfully.", ephemeral=True)
            else:
                await interaction.response.send_message("No members in the raid channel.", ephemeral=True)
                logging.info("No members to move in the raid channel.")
        else:
            await interaction.response.send_message("Configured channels are invalid.", ephemeral=True)
            logging.error("Configured channels are invalid.")
    else:
        await interaction.response.send_message("Raid or destination channel not set.", ephemeral=True)
        logging.warning("Raid or destination channel not set.")

@client.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.CheckFailure):
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        logging.warning(f"User '{interaction.user}' tried to use a command without sufficient permissions.")
    else:
        await interaction.response.send_message("An error occurred.", ephemeral=True)
        logging.error(f"An error occurred: {error}")
        raise error

# Read the bot token from an environment variable
if not TOKEN:
    logging.error("Bot token not found. Please set the DISCORD_BOT_TOKEN environment variable.")
else:
    client.run(TOKEN)
