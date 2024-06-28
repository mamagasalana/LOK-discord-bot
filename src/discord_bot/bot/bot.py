import discord
import logging
from discord.ext import commands, tasks
from discord_bot.bot.commands import VerifyButton
from discord_bot.services.lok_service import LokService
from discord.ui import View

class LOKBOT:
    def __init__(self):
        self.lokService = LokService()  # Initialize the LokService instance to handle external API interactions
        self.button = None # Button for user verification
        self.check_verification_mail_worker = None # Task for periodic checking

    def discord_bot(self, token, channel_id):
        """Initialize and run the Discord bot."""
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        
        # Initialize the bot with the specified command prefix and intents
        bot = commands.Bot(command_prefix='!', intents=intents)

        @bot.event
        async def on_ready():
            # https://discord.com/channels/{server id}/{channel id}
            try:
                channel = await bot.fetch_channel(channel_id)
                if channel:
                    await channel.send("Bot has joined the channel!")
                    self.button = VerifyButton()
                    view = View()
                    view.add_item(self.button)
                    await channel.send("Click the button to get your verification code:", view=view)
                    self.check_verification_mail_worker.start()
                else:
                    logging.error(f"Channel with ID {channel_id} not found.", exc_info=True)

            except discord.errors.NotFound:
                logging.error(f"Channel with ID {channel_id} not found.", exc_info=True)
            except discord.errors.Forbidden:
                logging.error(f"Bot does not have permission to access the channel with ID {channel_id}.", exc_info=True)
            except Exception as e:
                logging.error("Unknown exception - on ready", exc_info=True)

        @tasks.loop(seconds=1)
        async def check_verification_mail_worker():
            self.lokService.codes2discord.update(self.button.codes)
            if len(self.lokService.codes2LOK) != len(self.lokService.codes2discord):
                await self.lokService.get_verification_code_from_mail()

        self.check_verification_mail_worker = check_verification_mail_worker
        bot.run(token)

# Main entry point to start the bot
if __name__ == '__main__':
    from discord_bot.config.config import TOKEN, CHANNEL_ID
    lok_bot = LOKBOT()
    lok_bot.discord_bot(TOKEN, CHANNEL_ID)
