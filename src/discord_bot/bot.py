
import asyncio
from datetime import time
import datetime
import discord
from discord import app_commands
import logging
from discord.ext import commands, tasks
from discord_bot.commands import VerifyButton, MoreContentView
from discord_bot.autocomplete import autocomplete_requested_title, autocomplete_requested_resource, autocomplete_requested_monster
from services.lok_service_manager import LokServiceManager, LokService
from discord.ui import View
from config.config import TOKEN, CHANNEL_ID, GUILD_ID, CODE_EXPIRY_TIME, USER, PASSWORD
from db.resources.lok_resource_map import LOK_RESOURCE_MAP

class LOKBOT:
    def __init__(self):
        self.lokServiceManager = LokServiceManager()
        self.lokService = self.lokServiceManager.get_worker('teezai3')# Initialize the LokService instance to handle external API interactions
        self.verify_button = None  # Button for user verification
        self.check_verification_mail_worker = None  # Task for periodic checking
        self.CRYSTAL_MINE_LOADING = False

    def discord_bot(self, token, channel_id):
        """Initialize and run the Discord bot."""
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        bot = commands.Bot(command_prefix="/", intents=intents)  # Initialize the bot with the specified command prefix and intents
        guild = discord.Object(id=GUILD_ID)
        bot.tree.clear_commands(guild=None)
        bot.tree.clear_commands(guild=guild)

        # Define the slash command with two inputs and autocomplete for the second input
        @bot.tree.command(name="title", description="Set a title", guild=guild)
        @app_commands.describe( requested_title="Choose a title", your_kingdom_id="Your kingdom ID",)
        @app_commands.autocomplete(requested_title=autocomplete_requested_title)
        async def title(interaction: discord.Interaction, requested_title: str, your_kingdom_id: str):
            username = self.lokService.set_title(your_kingdom_id, requested_title)
            if username is None:
                await interaction.response.send_message(f"Kingdom ID: {your_kingdom_id} not found")
            else:
                await interaction.response.send_message(f"Title: {requested_title} assigned to {username}")

        @bot.tree.command(name="loc", description="set your lok location", guild=guild)
        @app_commands.describe( x="x-coordinate", y="y-coordinate")
        async def location(interaction: discord.Interaction, x: str, y: str):
            if not x.isnumeric() or not y.isnumeric():
                await interaction.response.send_message("Invalid coordinates. Please provide numeric values.", ephemeral=True)
                return
            self.lokServiceManager.set_user_location(interaction.user.id, x, y)
            await interaction.response.send_message("done", ephemeral=True)

        @bot.tree.command(name="mine", description="request crystal mine", guild=guild)
        @app_commands.describe(requested_resource="Choose a resource", required_level="level")
        @app_commands.autocomplete(requested_resource=autocomplete_requested_resource)
        async def mine(interaction: discord.Interaction, requested_resource: str = "Crystal", required_level: str = "1"):
            mine_id = LOK_RESOURCE_MAP.get(requested_resource)
            # Get the latest data
            mines = self.lokServiceManager.get_mine_for_user(interaction.user.id, datetime.datetime.now().replace(minute=9), mine_id=mine_id, level=int(required_level))
            if not mines:
                await interaction.response.send_message("Not found", ephemeral=True)
            await interaction.response.send_message(f"Requesting: {requested_resource}", ephemeral=True, view=MoreContentView(mines, interaction))

        @bot.tree.command(name="monster", description="request monster", guild=guild)
        @app_commands.describe(requested_monster="Choose a monster", required_level="level")
        @app_commands.autocomplete(requested_monster=autocomplete_requested_monster)
        async def monster(interaction: discord.Interaction, requested_monster: str , required_level: str = "1"):
            mine_id = LOK_RESOURCE_MAP.get(requested_monster)
            # Get the latest data
            mines = self.lokServiceManager.get_mine_for_user(interaction.user.id, datetime.datetime.now().replace(minute=9), mine_id=mine_id, level=int(required_level))
            if not mines:
                await interaction.response.send_message("Not found", ephemeral=True)
            await interaction.response.send_message(f"Requesting: {requested_monster}", ephemeral=True, view=MoreContentView(mines, interaction))

        @bot.event
        async def on_ready():
            # https://discord.com/channels/{guild id}/{channel id}
            get_crystal_mine_signal.start()
            # print_crystal_mine_signal.start()
            await bot.tree.sync()
            await bot.tree.sync(guild=guild)

            try:
                channel = await bot.fetch_channel(channel_id)
                if channel:
                    await channel.send("Bot has joined the channel!")
                    await channel.send("You can use /mine command to look for mine information!")
                    await channel.send("You can use /monster command to look for monster information!")
                    await channel.send("You can also use /loc command to set your location, this will further improve /mine search function")
                    status = self.lokServiceManager.get_worker_status()
                    await channel.send("############ Check worker status ##############")
                    await channel.send(f"{status}")
                    # await get_crystal_mine_signal(True)
                    # self.verify_button = VerifyButton()
                    # view = View()
                    # view.add_item(self.verify_button)
                    # await channel.send(
                    #     "Click the verify_button to get your verification code:",
                    #     view=view,
                    # )
                    # self.verify_button.start_verification_task(bot.loop)
                else:
                    logging.error(
                        f"Channel with ID {channel_id} not found.", exc_info=True
                    )

            except discord.errors.NotFound:
                logging.error(f"Channel with ID {channel_id} not found.", exc_info=True)
            except discord.errors.Forbidden:
                logging.error(
                    f"Bot does not have permission to access the channel with ID {channel_id}.",
                    exc_info=True,
                )
            except Exception as e:
                logging.error("Unknown exception - on ready", exc_info=True)

        
        @tasks.loop(minutes=1) 
        async def get_crystal_mine_signal(force=False):
            now = datetime.datetime.now()
            if now.hour == 0:
                # current server connection resets at 12
                return
            
            if now.minute == 10 or force:  # Run task at 10 minutes past the hour
            # if not self.CRYSTAL_MINE_LOADING :
                self.CRYSTAL_MINE_LOADING = True
                channel = await bot.fetch_channel(channel_id)
                # print divisor
                status = self.lokServiceManager.get_worker_status()
                await channel.send("############ Check worker status ##############")
                await channel.send(f"{status}")
                await channel.send("############ Updating mine database ##############")
                self.lokServiceManager.check_entire_map()
                # self.lokService.check_entire_map(start_y=0, end_y=2048)
                await self.lokServiceManager.start_wss()
                await channel.send("############ Done  ##############")
                self.CRYSTAL_MINE_LOADING = False

        # @tasks.loop(seconds=5)
        # async def print_crystal_mine_signal():
        #     dt = datetime.datetime.now() - datetime.timedelta(seconds=5)
        #     mines = self.lokServiceManager.get_mine(dt, level=2)
        #     channel = await bot.fetch_channel(channel_id)
        #     for m in mines:
        #         await channel.send(f"Crystal mine X:{m.x}, Y:{m.y}, level:{m.level}, occupied:{m.occupied}")

        @tasks.loop(seconds=5)  # Set the interval to 5 seconds
        async def check_verification_mail_worker():
            """Periodic task to check verification codes and print a message."""
            start_time = time.time()  # Record the start time
            while (time.time() - start_time) < CODE_EXPIRY_TIME:
                print("Checking verification codes...")  # Print a message every 5 seconds
                self.lokService.codes2discord.update(self.verify_button.codes)
                if len(self.lokService.codes2LOK) != len(self.lokService.codes2discord):
                    await self.lokService.get_verification_code_from_mail()
                await asyncio.sleep(5)  # Wait for 5 seconds before the next iteration
            self.check_verification_mail_worker.cancel()  # Stop the loop after the expiry time

        self.check_verification_mail_worker = check_verification_mail_worker
        bot.run(token)


# Main entry point to start the bot
if __name__ == "__main__":
    lok_bot = LOKBOT()
    lok_bot.discord_bot(TOKEN, CHANNEL_ID)
