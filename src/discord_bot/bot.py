
import asyncio
from datetime import time
import datetime
import discord
from discord import app_commands
import logging
from discord.ext import commands, tasks
from discord_bot.commands import VerifyButton, MoreContentView, LOKScreenerView
from discord_bot.autocomplete import autocomplete_requested_title, autocomplete_requested_charm
from services.lok_service_manager import LokServiceManager, LokService
from services.resourcefinder_service import ResourceFinder
from services.cache_service import BOT_CACHE

from config.config import TOKEN, CHANNEL_ID, GUILD_ID, CODE_EXPIRY_TIME, USER, PASSWORD, DEFAULT_WORLD
from db.resources.lok_resource_map import LOK_RESOURCE_MAP_INVERSE, COMMAND_ABBREVIATION, CHARM_MAP

class LOKBOT:

    def __init__(self):
        # self.lokServiceManager  =None
        # self.lokService = None
        self.lokServiceManager = LokServiceManager()
        self.lokServiceManager.switch_world(DEFAULT_WORLD)
        self.lokService = self.lokServiceManager.get_worker('teezai3')# Initialize the LokService instance to handle external API interactions
        self.verify_button = None  # Button for user verification
        self.check_verification_mail_worker = None  # Task for periodic checking
        self.CRYSTAL_MINE_LOADING = False
        self.CRYSTAL_MINE_LAST_UPDATE = None
        self.bot = None
        self.channel_id = CHANNEL_ID
        self.guild = discord.Object(id=GUILD_ID)
        self.main_message_content = """
            Bot has joined the channel!
            """
            # You can use /r + {prefix of resource} command to look for resource information!
            # etc: rc for Crystal, rl for Lumber
            # You can use /m + {prefix of monster} command to look for monster information!
            # etc: mg for Golem, mt for Treasure Goblin
            # You can also use /loc command to set your location, this will further improve the search function.
    
    def discord_bot(self, token):
        """Initialize and run the Discord bot."""
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        bot = commands.Bot(command_prefix="/", intents=intents)  # Initialize the bot with the specified command prefix and intents
        self.bot = bot

        bot.tree.clear_commands(guild=None)
        bot.tree.clear_commands(guild=self.guild)

        bot.tree.add_command(self.title_command, guild=self.guild)
        # bot.tree.add_command(self.set_location_command, guild=self.guild)
        # bot.tree.add_command(self.charm_command, guild=self.guild)
        # for command_name in COMMAND_ABBREVIATION:
        #     bot.tree.add_command(
        #         discord.app_commands.Command(
        #             name=command_name,
        #             description="Request resource/monster",
        #             callback=self.resource_monster_command
        #         ),
        #         guild=self.guild
        #     )

        @bot.event
        async def on_ready():
            # https://discord.com/channels/{guild id}/{channel id}
            # self.get_crystal_mine_signal.start()
            await bot.tree.sync()
            await bot.tree.sync(guild=self.guild)

            try:
                channel = await bot.fetch_channel(self.channel_id)
                if channel:
                    main_message_id = BOT_CACHE.load_message_id()
                    main_message = None

                    if main_message_id:
                        try:
                            main_message = await channel.fetch_message(main_message_id)
                        except:
                            pass

                    if not main_message:
                        try:
                            main_message = await channel.send(self.main_message_content, view=LOKScreenerView(self.get_crystal_mine_signal2))
                            await main_message.pin()
                            BOT_CACHE.save_message_id(main_message.id)
                        except discord.Forbidden:
                            print("Bot does not have permission to send or pin messages in the channel.")
                        except discord.HTTPException as e:
                            print(f"Failed to send or pin the message: {e}")

                    bot.add_view(LOKScreenerView(self.get_crystal_mine_signal2))
                    # await channel.send(self.welcome_message, view=LOKScreenerView())
                    # status = self.lokServiceManager.get_worker_status()
                    # await channel.send("############ Check worker status ##############\n"
                    #                    f"{status}"
                    #                    )
                    
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
                        f"Channel with ID {self.channel_id} not found.", exc_info=True
                    )

            except discord.errors.NotFound:
                logging.error(f"Channel with ID {self.channel_id} not found.", exc_info=True)
            except discord.errors.Forbidden:
                logging.error(
                    f"Bot does not have permission to access the channel with ID {self.channel_id}.",
                    exc_info=True,
                )
            except Exception as e:
                logging.error("Unknown exception - on ready", exc_info=True)

        bot.run(token)

    @property
    def title_command(self):
        # Define the slash command with two inputs and autocomplete for the second input
        @app_commands.command(name="title",description="Set a title")
        @app_commands.describe( requested_title="Choose a title", your_kingdom_id="Your kingdom ID",)
        @app_commands.autocomplete(requested_title=autocomplete_requested_title)
        async def title(interaction: discord.Interaction, requested_title: str, your_kingdom_id: str):
            username = self.lokService.set_title(your_kingdom_id, requested_title)
            if username is None:
                await interaction.response.send_message(f"Kingdom ID: {your_kingdom_id} not found")
            else:
                await interaction.response.send_message(f"Title: {requested_title} assigned to {username}")
        return title

    @property
    def set_location_command(self):
        @app_commands.command(name="loc", description="set your lok location")
        @app_commands.describe(world="world", x="x-coordinate", y="y-coordinate")
        async def location(interaction: discord.Interaction, world:str, x: str, y: str):
            if not x.isnumeric() or not y.isnumeric():
                await interaction.response.send_message("Invalid coordinates. Please provide numeric values.", ephemeral=True)
                return
            ResourceFinder.set_user_location(interaction.user.id, world, x, y)
            await interaction.response.send_message("done", ephemeral=True)
        return location
    
    @property
    def resource_monster_command(self):
        @app_commands.describe(required_level="level")
        async def resource(interaction: discord.Interaction, required_level: str='1'):
            command_name = interaction.command.name
            mine_id = COMMAND_ABBREVIATION.get(command_name)
            requested_resource  = LOK_RESOURCE_MAP_INVERSE.get(mine_id)
            # Get the latest data
            mines = ResourceFinder.get_mine_for_user(interaction.user.id, mine_id=mine_id, level=int(required_level))
            if not mines:
                await interaction.response.send_message("Not found", ephemeral=True)
            await interaction.response.send_message(f"Requesting: {requested_resource}", ephemeral=True, view=MoreContentView(mines, interaction))

        return resource

    @property
    def charm_command(self):
        @app_commands.command(name="charm",description="Request charm")
        @app_commands.describe(requested_charm="Charm Type", required_level="Charm Level" )
        @app_commands.autocomplete(requested_charm=autocomplete_requested_charm)
        async def charm(interaction: discord.Interaction, requested_charm: str, required_level: str='1'):
            charm_id = CHARM_MAP.get(requested_charm)
            # Get the latest data
            mines = ResourceFinder.get_charm_for_user(interaction.user.id, charm_id=charm_id, level=int(required_level))
            if not mines:
                await interaction.response.send_message("Not found", ephemeral=True)
            await interaction.response.send_message(f"Requesting: {requested_charm}", ephemeral=True, view=MoreContentView(mines, interaction))

        return charm
    
    async def get_crystal_mine_signal2(self, interaction: discord.Interaction):
        now = datetime.datetime.now()
        user = interaction.user.id
        world = ResourceFinder.get_user_location(user)
        if world:
            self.lokServiceManager.switch_world(world)
        else:
            self.lokServiceManager.switch_world(DEFAULT_WORLD)
            
        if now.hour == 0 and now.minute < 20:
            # current server connection resets at 12
            await interaction.response.send_message("Server is sleeping, refuse to update database", ephemeral=True)
            return
        
        if self.CRYSTAL_MINE_LOADING :
            await interaction.response.send_message("Server is still updating database, please be patient", ephemeral=True)
            return 
        
        if self.CRYSTAL_MINE_LAST_UPDATE is not None:
            time_passed = now - self.CRYSTAL_MINE_LAST_UPDATE
            remaining_time = datetime.timedelta(hours=1) - time_passed
            if remaining_time > datetime.timedelta(seconds=0):
                # Format the remaining time as minutes and seconds
                minutes = remaining_time.seconds // 60
                seconds = remaining_time.seconds % 60
                await interaction.response.send_message(f"You still need to wait {minutes} minutes and {seconds} seconds.", ephemeral=True)
                return 
        
        self.CRYSTAL_MINE_LAST_UPDATE =  now
        await interaction.response.send_message("Updating database ...", ephemeral=True)     
        self.CRYSTAL_MINE_LOADING = True

        if world > 100_000: # cvc
            # the crystal is around the corner
            # look for the adjacent corner
            self.lokServiceManager.check_entire_map(start_x=0, end_x=13, start_y=0, end_y = 400)
            self.lokServiceManager.check_entire_map(start_x=50, end_x=63, start_y=0, end_y = 400)
            self.lokServiceManager.check_entire_map(start_x=0, end_x=13, start_y=1600, end_y = 2000)
            self.lokServiceManager.check_entire_map(start_x=50, end_x=63, start_y=1600, end_y = 2000)
        else:
            self.lokServiceManager.check_entire_map()
        # self.lokService.check_entire_map(start_y=0, end_y=2048)
        await self.lokServiceManager.start_wss()

        timespent = datetime.datetime.now() - now
        minutes = timespent.seconds // 60
        seconds = timespent.seconds % 60
        logging.info(f"Database update complete. Used {minutes} minutes and {seconds} seconds.")
        await interaction.followup.send(f"Database update complete. Used {minutes} minutes and {seconds} seconds.", ephemeral=True)
        self.CRYSTAL_MINE_LOADING = False

    # @tasks.loop(minutes=1) 
    # async def get_crystal_mine_signal(self, force=False):
    #     now = datetime.datetime.now()
    #     if now.hour == 0:
    #         # current server connection resets at 12
    #         return
        
    #     if now.minute == 10 or force:  # Run task at 10 minutes past the hour
    #     # if not self.CRYSTAL_MINE_LOADING :
    #         self.CRYSTAL_MINE_LOADING = True
    #         channel = await self.bot.fetch_channel(self.channel_id)
    #         # print divisor
    #         status = self.lokServiceManager.get_worker_status()
    #         await channel.send("############ Check worker status ##############")
    #         await channel.send(f"{status}")
    #         await channel.send("############ Updating mine database ##############")
    #         self.lokServiceManager.check_entire_map()
    #         # self.lokService.check_entire_map(start_y=0, end_y=2048)
    #         await self.lokServiceManager.start_wss()
    #         await channel.send("############ Done  ##############")
    #         self.CRYSTAL_MINE_LOADING = False


        # @tasks.loop(seconds=5)  # Set the interval to 5 seconds
        # async def check_verification_mail_worker():
        #     """Periodic task to check verification codes and print a message."""
        #     start_time = time.time()  # Record the start time
        #     while (time.time() - start_time) < CODE_EXPIRY_TIME:
        #         print("Checking verification codes...")  # Print a message every 5 seconds
        #         self.lokService.codes2discord.update(self.verify_button.codes)
        #         if len(self.lokService.codes2LOK) != len(self.lokService.codes2discord):
        #             await self.lokService.get_verification_code_from_mail()
        #         await asyncio.sleep(5)  # Wait for 5 seconds before the next iteration
        #     self.check_verification_mail_worker.cancel()  # Stop the loop after the expiry time

        # self.check_verification_mail_worker = check_verification_mail_worker
        

# Main entry point to start the bot
if __name__ == "__main__":
    lok_bot = LOKBOT()
    lok_bot.discord_bot(TOKEN)
