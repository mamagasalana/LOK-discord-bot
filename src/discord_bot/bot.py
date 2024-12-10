
if __name__ == "__main__":
    import os
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from datetime import time
import datetime
import discord
from discord import app_commands
import logging
from discord.ext import commands, tasks
from discord_bot.commands import VerifyButton
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
        ALLOWED_TITLES = [
            {'name': 'Alchemist', 'emoji': '🔮'}, 
            {'name': 'Architect', 'emoji': '🏛️'}
        ]
        ALLOWED_RESOURCES = [
            {'name': 'Crystal', 'emoji': '💎'}, 
            {'name': 'Lumber', 'emoji': '🌲'}
        ]


        async def autocomplete_requested_title(interaction: discord.Interaction, current: str):
            return [
                app_commands.Choice(
                    name=f"{title['emoji']} {title['name']}", 
                    value=title['name']
                )
                for title in ALLOWED_TITLES if current.lower() in title['name'].lower()
            ]

        # Autocomplete function for resources
        async def autocomplete_requested_resource(interaction: discord.Interaction, current: str):
            return [
                app_commands.Choice(
                    name=f"{resource['emoji']} {resource['name']}", 
                    value=resource['name']
                )
                for resource in ALLOWED_RESOURCES if current.lower() in resource['name'].lower()
            ]
        
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

        @bot.tree.command(name="mine", description="request crystal mine", guild=guild)
        @app_commands.describe( requested_resource="Choose a resource", required_level="level")
        @app_commands.autocomplete(requested_resource=autocomplete_requested_resource)
        async def title(interaction: discord.Interaction, requested_resource: str, required_level: str):
            mine_id = LOK_RESOURCE_MAP.get(requested_resource)
            # only return latest data
            mines = self.lokServiceManager.get_mine(datetime.datetime.now().replace(minute=9), mine_id=mine_id, level=int(required_level))
            resp = []
            resp.append(f"Requested: {requested_resource}")
            if not mines:
                resp.append(f"Not found")

            for m in mines:
                resp.append(f"X:{m.x}, Y:{m.y}, level:{m.level}, occupied:{m.occupied}")

            count= 0
            resp_regroup = []
            for r in resp:
                #discord has a message limit of 2000
                current_count = len(r) +1
                if (count ==0) or (current_count + count >= 2000):
                    resp_regroup.append([])
                    count = 0

                resp_regroup[-1].append(r)
                count += current_count

            for idx, r in enumerate(resp_regroup):
                chunk = '\n'.join(r)
                if idx == 0:
                    await interaction.response.send_message(chunk)  # First message
                else:
                    await interaction.followup.send(chunk)  # Subsequent messages

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
                    await channel.send("You can you /mine command to look for mine information!")
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
