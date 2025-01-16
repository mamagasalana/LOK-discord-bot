from discord import app_commands
import discord

ALLOWED_TITLES = [
    {'name': 'Alchemist', 'emoji': '🔮'}, 
    {'name': 'Architect', 'emoji': '🏛️'}
]
ALLOWED_RESOURCES = [
    {'name': 'Farm', 'emoji': '🌽'}, 
    {'name': 'Crystal', 'emoji': '💎'}, 
    {'name': 'Gold', 'emoji': '💰'}, 
    {'name': 'Lumber', 'emoji': '🌲'},
    {'name': 'Quarry', 'emoji': '⛰️'}
]

ALLOWED_MONSTER = [
    {'name': 'Orc', 'emoji': '🪓'}, 
    {'name': 'Skeleton', 'emoji': '☠️'}, 
    {'name': 'Golem', 'emoji': '🗿'}, 
    {'name': 'Goblin', 'emoji': '👹'},
]

ALLOWED_CHARM = [
    {'name': 'Harvester', 'emoji': '🌾'},
    {'name': 'Lumberjack', 'emoji': '🌲'},
    {'name': 'Stonecraft', 'emoji': '🪨'},
    {'name': 'Goldmine', 'emoji': '⛏️'},
    {'name': 'Scholar', 'emoji': '📚'},
    {'name': 'Resource', 'emoji': '🌱'},  # gathering
    {'name': 'Builder', 'emoji': '🔨'},
    {'name': 'Trainer', 'emoji': '🏋️'},
    {'name': 'Stamina', 'emoji': '💪'},  # hp
    {'name': 'Attacker', 'emoji': '⚔️'},
    {'name': 'Speed', 'emoji': '⚡'},
    {'name': 'Load', 'emoji': '📦'},
    {'name': 'Energy', 'emoji': '💥'},  # action point
    {'name': 'Defender', 'emoji': '🛡️'},
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

# Autocomplete function for monster
async def autocomplete_requested_monster(interaction: discord.Interaction, current: str):
    return [
        app_commands.Choice(
            name=f"{monster['emoji']} {monster['name']}", 
            value=monster['name']
        )
        for monster in ALLOWED_MONSTER if current.lower() in monster['name'].lower()
    ]

# Autocomplete function for charm
async def autocomplete_requested_charm(interaction: discord.Interaction, current: str):
    return [
        app_commands.Choice(
            name=f"{charm['name']}{charm['emoji']} ", 
            value=charm['name']
        )
        for charm in ALLOWED_CHARM if current.lower() in charm['name'].lower()
    ]