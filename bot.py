import asyncio
import os
import discord
from discord import app_commands
from discord import Intents
from discord import Client
import logging
import argparse
import config
from process import charutil

import util

from discord import app_commands
from dotenv import load_dotenv
from observer import observer
from model import apiconfig
load_dotenv()
discord_token:str = os.getenv("DISCORD_TOKEN")

intents: Intents = discord.Intents.default()
intents.message_content = True

client:Client = discord.Client(command_prefix='/', intents=intents)
tree:app_commands.CommandTree = app_commands.CommandTree(client)


#AND THIS!!! Is where they set things up!
#Like, dude, come on!  In the middle of the file!? Really!?!?!?
@client.event
async def on_ready():
    # Let owner known in the console that the bot is now running!
    print(f'Discord Bot is Loading...')

    logging.basicConfig(level=logging.DEBUG)

    config.text_api = await apiconfig.set_api("text-default.json")
    if config.text_api["name"] != "openai":
        api_check = await apiconfig.api_status_check(config.text_api["address"] + config.text_api["model"], headers=config.text_api["headers"])

    #config.character_card = await charutil.get_character_prompt("default")

    asyncio.create_task(apiconfig.send_to_model_queue())
    asyncio.create_task(apiconfig.send_to_stable_diffusion_queue())
    asyncio.create_task(apiconfig.send_to_user_queue())

    # Sync current slash commands (commented out unless we have new commands)
    # tree.add_command(personality)
    # tree.add_command(history)
    # tree.add_command(character)
    # await tree.sync()

    print(f'Discord Bot is up and running.')


@client.event
async def on_message(message):

    if message is None:
        return
    
    # Bot will now either do or not do something!
    print("Message Get")
    await observer.bot_behavior(message, client)

# Slash command to update the bot's personality
personality : app_commands.Group= app_commands.Group(
    name="personality", description="View or change the bot's personality.")


@personality.command(name="view", description="View the bot's personality profile.")
async def view_personality(interaction):
    # Display current personality.
    await interaction.response.send_message("The bot's current personality: **" + character_card["persona"] + "**.")


@personality.command(name="set", description="Change the bot's personality.")
@app_commands.describe(persona="Describe the bot's new personality.")
async def edit_personality(interaction, persona: str):
    global character_card

    # Update the global variable
    old_personality = character_card["persona"]
    character_card["persona"] = persona

    # Display new personality, so we know where we're at
    await interaction.response.send_message("Bot's personality has been updated from \"" + old_personality + "\" to \"" + character_card["persona"] + "\".")


@personality.command(name="reset", description="Reset the bot's personality to the default.")
async def reset_personality(interaction):
    global character_card

    # Update the global variable
    old_personality = character_card["persona"]
    #character_card = await charutil.get_character_prompt("default.json")

    # Display new personality, so we know where we're at
    await interaction.response.send_message("Bot's personality has been updated from \"" + old_personality + "\" to \"" + character_card["persona"] + "\".")

# Slash commands to update the conversation history
history = app_commands.Group(
    name="conversation-history", description="View or change the bot's personality.")


@history.command(name="reset", description="Reset your conversation history with the bot.")
async def reset_history(interaction):
    user = str(interaction.user.display_name)
    user = user.replace(" ", "")
    user = util.clean_username(user)

    file_name = util.get_file_name("context", user + ".txt")

    # Attempt to remove the file and let the user know what happened.
    try:
        os.remove(file_name)
        await interaction.response.send_message("Your conversation history was deleted.")
    except FileNotFoundError:
        await interaction.response.send_message("There was no history to delete.")
    except PermissionError:
        await interaction.response.send_message("The bot doesn't have permission to reset your history. Let bot owner know.")
    except Exception as e:
        print(e)
        await interaction.response.send_message("Something has gone wrong. Let bot owner know.")


@history.command(name="view", description=" View the last 20 lines of your conversation history.")
async def view_history(interaction):
    # Get the user who started the interaction and find their file.

    user = str(interaction.user.display_name)
    user = user.replace(" ", "")
    user = util.clean_username(user)

    file_name = util.get_file_name("context", user + ".txt")

    try:
        with open(file_name, "r", encoding="utf-8") as file:  # Open the file in read mode
            contents = file.readlines()
            contents = contents[-20:]
            history_string = ''.join(contents)
            await interaction.response.send_message(history_string)
    except FileNotFoundError:
        await interaction.response.send_message("You have no history to display.")
    except Exception as e:
        print(e)
        await interaction.response.send_message("Message history is more than 2000 characters and can't be displayed.")

# Slash commands for character card presets (if not interested in manually updating)
character = app_commands.Group(
    name="character-cards", description="View or changes the bot's current character card, including name and image.")

# Command to view a list of available characters.

async def parameter_select_callback(interaction):

    await interaction.response.defer()

    # Get the value selected by the user via the dropdown.
    selection = interaction.data.get("values", [])[0]

    # Adjust the character card for the bot to match what the user selected.
    config.text_api = await apiconfig.set_api(selection)
    api_check = await apiconfig.api_status_check(config.text_api["address"] + config.text_api["model"], headers=config.text_api["headers"])

    # Let the user know that their request has been completed
    await interaction.followup.send(interaction.user.name + " updated the bot's sampler parameters. " + api_check)

parser = argparse.ArgumentParser(
    description='AI Discord bot, use --tts_xtts to enable XTTS')
parser.add_argument('--tts_xtts', action='store_true',
                    help='Flag to disable TTS (XTTS)')
args = parser.parse_args()
enable_tts_global = args.tts_xtts

client.run(discord_token)
# unittest.main()
