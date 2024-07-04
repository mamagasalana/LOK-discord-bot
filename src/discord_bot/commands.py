import discord
from discord.ui import Button
import random
import string
import time
from src.config.config import CODE_EXPIRY_TIME, DYNAMO_DB_NAME
from db.repository.verification_code_repository import VerificationCodeRepository


class VerifyButton(Button):
    def __init__(self):
        super().__init__(label="Verify", style=discord.ButtonStyle.primary)
        self.codes = {}
        self.user_cool_down = {}  # Track when users last clicked the button
        self.cool_down_duration = int(CODE_EXPIRY_TIME)  # Cool down duration in seconds
        self.verification_code_repo = VerificationCodeRepository(DYNAMO_DB_NAME)

    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        current_time = time.time()

        # Check if the user is on cool down
        if user_id in self.user_cool_down:
            last_click_time = self.user_cool_down[user_id]
            if current_time - last_click_time < self.cool_down_duration:
                # User is on cool down, inform them to wait
                await interaction.response.send_message("Please wait 60 seconds before clicking verify again.", ephemeral=True)
                return

        # Generate a unique confirmation code
        code = None
        while code is None or code in self.codes:
            code = self.generate_confirmation_code()
        self.codes[code] = [interaction.user.name, interaction.user.global_name, interaction.id]

        # Update the user's last click time
        self.user_cool_down[user_id] = current_time

        # Define the message
        verification_message = f'Send verification code to account ClosureM at location 1153:906.\n\nCode: {code}'

        # Send verification message in the channel
        await interaction.response.send_message(verification_message, ephemeral=True)
                                                
        # Send direct verification message to the user
        if interaction.user.dm_channel is None:
            await interaction.user.create_dm()
        await interaction.user.dm_channel.send(verification_message)

        # Add verification code to DynamoDB
        item = self.verification_code_repo.create_verification_code(user_id, code)

    def generate_confirmation_code(self, length=6):
        letters_and_digits = string.ascii_letters + string.digits
        return ''.join(random.choice(letters_and_digits) for _ in range(length))
