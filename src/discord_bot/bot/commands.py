import discord
from discord.ui import Button
import random
import string

class VerifyButton(Button):
    def __init__(self):
        super().__init__(label="Verify", style=discord.ButtonStyle.primary)
        self.codes = {}

    def generate_confirmation_code(self, length=6):
        letters_and_digits = string.ascii_letters + string.digits
        return ''.join(random.choice(letters_and_digits) for _ in range(length))

    async def callback(self, interaction: discord.Interaction):
        code = None
        while code is None or code in self.codes:
            code = self.generate_confirmation_code()
        self.codes[code] = [interaction.user.name, interaction.user.global_name, interaction.id]
        await interaction.response.send_message(f'Your confirmation code is: {code}', ephemeral=True)
