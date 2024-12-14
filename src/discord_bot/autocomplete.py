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