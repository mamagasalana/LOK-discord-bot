import asyncio
from datetime import time
import discord
import logging
from discord.ext import commands, tasks
from discord_bot.commands import VerifyButton
from services.lok_service import LokService
from discord.ui import View
from src.config.config import TOKEN, CHANNEL_ID, CODE_EXPIRY_TIME


class LOKBOT:
    def __init__(self):
        self.lokService = (
            LokService()
        )  # Initialize the LokService instance to handle external API interactions
        self.verify_button = None  # Button for user verification
        self.check_verification_mail_worker = None  # Task for periodic checking

    def discord_bot(self, token, channel_id):
        """Initialize and run the Discord bot."""
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        bot = commands.Bot(
            command_prefix="!", intents=intents
        )  # Initialize the bot with the specified command prefix and intents

        @bot.event
        async def on_ready():
            # https://discord.com/channels/{server id}/{channel id}
            try:
                channel = await bot.fetch_channel(channel_id)
                if channel:
                    await channel.send("Bot has joined the channel!")
                    self.verify_button = VerifyButton()
                    view = View()
                    view.add_item(self.verify_button)
                    await channel.send(
                        "Click the verify_button to get your verification code:",
                        view=view,
                    )
                    self.verify_button.start_verification_task(bot.loop)
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
