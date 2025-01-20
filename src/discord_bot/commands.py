from discord.ui import Button, View, button, Select, TextInput, Modal
import random
import string
import time
from config.config import CODE_EXPIRY_TIME, DYNAMO_DB_NAME
from db.repository.verification_code_repository import VerificationCodeRepository
from discord import Interaction, ButtonStyle, SelectOption
from db.resources.lok_resource_map import LOK_RESOURCE_MAP_INVERSE, LOK_RESOURCE_MAP, HEADER_MAP, CHARM_MAP_INVERSE, CHARM_MAP
from discord_bot.autocomplete import ALLOWED_CHARM, ALLOWED_MONSTER, ALLOWED_RESOURCES
from db.resources.mine import Mine
from typing import Iterator
from services.resourcefinder_service import ResourceFinder
from services.cache_service import BOT_CACHE

USER_CACHE= BOT_CACHE.load_user_selection()

class VerifyButton(Button):
    def __init__(self):
        super().__init__(label="Verify", style=ButtonStyle.primary)
        self.codes = {}
        self.user_cool_down = {}  # Track when users last clicked the button
        self.cool_down_duration = int(CODE_EXPIRY_TIME)  # Cool down duration in seconds
        self.verification_code_repo = VerificationCodeRepository(DYNAMO_DB_NAME)

    async def callback(self, interaction: Interaction):
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


class MoreContentView(View):
    def __init__(self, list_of_resource:Iterator[list[Mine]], interaction: Interaction):
        super().__init__(timeout=None)
        self.mines = list_of_resource
        self.interaction = interaction

        self.b1 = Button(label="More...", style=ButtonStyle.primary)
        self.b1.callback = self.more_button
        self.add_item(self.b1)

    async def more_button(self, interaction: Interaction):
        try:
            item = next(self.mines)
            ret = []
            for m in item:
                header= HEADER_MAP.get(str(m.code)[:6])
                if header == 'c':
                    m_name = CHARM_MAP_INVERSE.get(m.charmcode)
                else:
                    m_name = LOK_RESOURCE_MAP_INVERSE.get(m.code)
                ret.append(f"{m_name.ljust(20)}| X:{m.x}, Y:{m.y}, level:{m.level}")
            chunk=  '\n'.join(ret)
            await self.interaction.edit_original_response(view=None)
            await interaction.response.send_message(chunk, ephemeral=True, view=MoreContentView(self.mines, interaction))

        except StopIteration:
            await interaction.response.send_message("end of search", ephemeral=True)
            self.b1.disabled = True
            await self.interaction.edit_original_response(view=self)

class LocationModal(Modal):
    def __init__(self):
        super().__init__(title="Enter Coordinates: ")
        self.loc_x = TextInput(label="X", placeholder="X")
        self.loc_y = TextInput(label="Y", placeholder="Y")

        self.loc_x.callback = self.text_callback
        self.loc_y.callback = self.text_callback

        self.add_item(self.loc_x)
        self.add_item(self.loc_y)

    async def text_callback(self, interaction: Interaction):
        await interaction.response.defer()

    async def on_submit(self, interaction: Interaction):
        x = self.loc_x.value
        y = self.loc_y.value
        if not x.isnumeric() or not y.isnumeric():
            await interaction.response.send_message("Invalid coordinates. Please provide numeric values.", ephemeral=True)
            return

        ResourceFinder.set_user_location(interaction.user.id, x, y)
        await interaction.response.send_message("done", ephemeral=True)

class LOKScreenerView(View):
    def __init__(self, crystal_mine_callback):
        # Set timeout=None for persistent view
        super().__init__(timeout=None)
        b_resource = Button(label="Resource Screener", style=ButtonStyle.primary, custom_id="main:open_form1")
        b_monster = Button(label="Monster Screener", style=ButtonStyle.primary, custom_id="main:open_form2")
        b_charm = Button(label="Charm Screener", style=ButtonStyle.primary, custom_id="main:open_form3")
        b_loc = Button(label="Set Location", style=ButtonStyle.primary, custom_id="main:open_form4")
        b_update = Button(label="Update Database", style=ButtonStyle.primary, custom_id="main:open_form5")

        b_resource.callback = self.open_form_resource
        b_monster.callback = self.open_form_monster
        b_charm.callback = self.open_form_charm
        b_loc.callback = self.open_form_loc
        b_update.callback = crystal_mine_callback
        self.add_item(b_resource);  self.add_item(b_monster); self.add_item(b_charm); self.add_item(b_loc); self.add_item(b_update)

    async def open_form_resource(self, interaction: Interaction):
        view = ScreenerView(interaction.user.id, 'resource')
        await interaction.response.send_message("Resource Screener:", view=view, ephemeral=True)

    
    async def open_form_monster(self, interaction: Interaction):
        view = ScreenerView(interaction.user.id, 'monster')
        await interaction.response.send_message("Monster Screener:", view=view, ephemeral=True)

    
    async def open_form_charm(self, interaction: Interaction):
        view = ScreenerView(interaction.user.id, 'charm')
        await interaction.response.send_message("Charm Screener:", view=view, ephemeral=True)

    async def open_form_loc(self, interaction: Interaction):
        modal = LocationModal()
        await interaction.response.send_modal(modal)


class ScreenerView(View):
    def __init__(self, userid, category):
        super().__init__()  
        self.category = category
        userid = str(userid)
        if userid not in USER_CACHE:
            USER_CACHE[userid]= {
                        'resource': [],
                        'resource_level': [],
                        'charm': [],
                        'charm_level': [],
                        'monster': [],
                        'monster_level': [],
                        }
        selected = USER_CACHE.get(userid)
        
        category_map = {
            'resource' : ALLOWED_RESOURCES,
            'monster' : ALLOWED_MONSTER,
            'charm' : ALLOWED_CHARM
        }
        options=[SelectOption(label=x['emoji']+x['name'], value=x['name'], default=x['name'] in selected[category]) for x in category_map.get(category)]

        if category =='charm':
            options_level = [
                SelectOption(label=x, value=x, default=x in selected['%s_level' % category]) 
                for x in range(1, 5)]
        else:
            options_level = [
                SelectOption(label=x, value=x, default=str(x) in selected['%s_level' % category]) 
                for x in range(1, 11)]

        self.select = Select(placeholder="%s ..." % category,min_values=1,max_values=len(options),options=options)
        self.level_select = Select(placeholder="%s Level..." % category,min_values=1,max_values=len(options_level),options=options_level)

        self.select.callback = self.select_callback
        self.level_select.callback = self.select_level_callback

        self.add_item(self.select)
        self.add_item(self.level_select)

        # Add the submit button
        self.submit_button = Button(
            label="Submit", style=ButtonStyle.success)
        
        self.submit_button.callback = self.submit_callback
        self.add_item(self.submit_button)

    async def select_callback(self, interaction: Interaction):
        USER_CACHE[str(interaction.user.id)]['%s' % self.category] = self.select.values
        await interaction.response.defer()

    async def select_level_callback(self, interaction: Interaction):
        USER_CACHE[str(interaction.user.id)]['%s_level' % self.category] = self.level_select.values
        await interaction.response.defer()

    async def submit_callback(self, interaction: Interaction):
        userid = str(interaction.user.id)
        level = USER_CACHE[userid]['%s_level' % self.category]
        mine = USER_CACHE[userid]['%s' % self.category]
        BOT_CACHE.save_user_selection(USER_CACHE)
        if self.category == 'charm':
            mine_code = [CHARM_MAP.get(x) for x in mine]
            mines =ResourceFinder.get_charm_for_user(userid, mine_code, level)
        else:
            mine_code = [LOK_RESOURCE_MAP.get(x) for x in mine]
            mines =ResourceFinder.get_mine_for_user(userid, mine_code, level)

        if not mines:
            await interaction.response.send_message("Not found", ephemeral=True)
        await interaction.response.edit_message(content=f"Requesting: {mine}", view=MoreContentView(mines, interaction))

if __name__ =='__main__':
    import discord
    from discord.ext import commands
    CHANNEL_ID = 1255170078497050628  # Replace with your channel ID

    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True
    intents.members = True

    bot = commands.Bot(command_prefix="!", intents=intents)
    @bot.event
    async def on_ready():
        print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
        view = LOKScreenerView()
        channel = bot.get_channel(CHANNEL_ID)
        await channel.purge(limit=10)
        await channel.send("Please select roles to apply:", view=view)

    bot.run('MTI1NTE2MzQ2MDg2NjU0MzY3Mg.Ghena7.GBqRf0wxoaVfuQcEGhZmHY0r09-DlLDyiUJOVM')