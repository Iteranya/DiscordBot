import asyncio
import os
import re
import process.charutil as charutil
import process.multimodal as multimodal
from model import apiconfig
import config
import discord
import util
from io import BytesIO
import io
import json
from PIL import Image
from PIL import Image
from process import qutil
from process import history
from typing import Any
from process import lam
# This part decides what to do with the incoming message
# Also LAM stuff~(coming soon)
inline_comprehension = True
async def think() -> None:

    while True:
        content = await config.queue_to_process_everything.get()
        message:discord.message.Message = content["message"]
        bot = content["bot"]
        if isinstance(message.channel, discord.DMChannel):
            continue
        elif isinstance(message.channel,discord.Thread):
            channel_name = message.channel.name
            dimension = createOrFetchJson(sanitize_string(channel_name))
            try:
                
                await message.add_reaction('✨')
            except Exception as e:
                print(e)

            json_card = await charutil.get_card(bot)
            message_content = message.content # This is the string message
            
            if json_card is None:
                pass
            
            if message_content.startswith(">"):
                await send_lam_message(message,json_card)
            elif message_content.startswith("//"):
                pass
            elif message_content.startswith("^"):
                await send_positional_message(message_content,dimension)
            elif message.attachments:
                if(config.florence):
                    await send_multimodal_message(message,json_card,dimension)
                else:
                    await send_llm_message(message, json_card,dimension)
            else:
                await send_llm_message(message, json_card,dimension)
            config.queue_to_process_everything.task_done()
        elif isinstance(message.channel,discord.channel.TextChannel):
            channel_name = message.channel.name
            dimension = createOrFetchJson(sanitize_string(channel_name))
            try:
                
                await message.add_reaction('✨')
            except Exception as e:
                print(e)

            json_card = await charutil.get_card(bot)
            message_content = message.content # This is the string message
            
            if json_card is None:
                pass
            
            if message_content.startswith(">"):
                await send_lam_message(message,json_card)
            elif message_content.startswith("//"):
                pass
            elif message_content.startswith("^"):
                await send_positional_message(message_content,dimension)
            elif message.attachments:
                if(config.florence):
                    await send_multimodal_message(message,json_card,dimension)
                else:
                    await send_llm_message(message, json_card,dimension)
            else:
                await send_llm_message(message, json_card,dimension)
            config.queue_to_process_everything.task_done()

async def send_multimodal_message(message:discord.message, json_card,dimension):
    print("Multimodal Processing...")
    image_sys_message = await qutil.get_image_message_queue_item(message)
    context = await history.get_channel_history(message.channel)
    if inline_comprehension:
        context+="\n"+str(image_sys_message["content"])
    else:
        await apiconfig.send_to_discord(image_sys_message)
    
    text_bot_prompt = await qutil.get_text_prompt_queue_item(message,json_card,context,dimension)
    llm_response = await apiconfig.send_to_model_queue(text_bot_prompt)
    await apiconfig.send_to_discord(llm_response)
    return


async def send_llm_message(message,json_card,dimension):
    print("Chat Completion Processing...")
    context = await history.get_channel_history(message.channel)
    text_bot_prompt = await qutil.get_text_prompt_queue_item(message,json_card,context,dimension)
    llm_response = await apiconfig.send_to_model_queue(text_bot_prompt)
    await apiconfig.send_to_discord(llm_response)
    return

async def send_lam_message(message, json_card):
    print("LAM Processing...")
    context = await history.get_channel_history(message.channel)
    thoughts = "Alright then..."
    action_bot_prompt = await qutil.get_action_prompt_queue_item(context, thoughts, message, json_card)
    lam_response = await apiconfig.send_to_model_queue(action_bot_prompt)
    await lam.process_action(lam_response, message)

    return

async def send_positional_message(message:str,dimension):
    print("Positional Processing...")
    if message.startswith("^get"):
        await apiconfig.send_to_discord({
                "response":dimension["description"]
            })
    elif message.startswith("^set"):
        dimension["description"] = message
        replaceJsonContent(dimension["name"], dimension)
    else:
        pass  
    return

def createOrFetchJson(input_string):
    # File name with .json extension
    file_name = f"channels/{input_string}.json"

    # Check if the file already exists
    if os.path.exists(file_name):
        # Open and fetch the content
        with open(file_name, "r") as json_file:
            data = json.load(json_file)
        print(f"File '{file_name}' already exists. Fetched content: {data}")
        return data
    
    # If it doesn't exist, create the data and save it
    data = {
        "name": input_string,
        "description":"[System Note: Takes place in a discord text channel]",
        "global":"[System Note: Takes place in a discord server]",
        "instruction":"[System Note: Takes place in a discord text channel]"
        }
    with open(file_name, "w") as json_file:
        json.dump(data, json_file, indent=4)
    print(f"File '{file_name}' created with content: {data}")
    return data

def replaceJsonContent(file_name, new_content):
    """Replaces the content of the JSON file with a given dictionary."""
    # Ensure the file name ends with .json
    if not file_name.endswith(".json"):
        file_name += ".json"
    
    # Check if the file exists
    if not os.path.exists("channels/"+file_name):
        print(f"File '{file_name}' does not exist. Cannot replace content.")
        return None

    # Ensure new_content is a dictionary
    if not isinstance(new_content, dict):
        raise ValueError("New content must be a dictionary.")

    # Replace the content
    with open("channels/"+file_name, "w") as json_file:
        json.dump(new_content, json_file, indent=4)
    print(f"File '{file_name}' content replaced with: {new_content}")
    return new_content

def sanitize_string(input_string):

    sanitized_string = re.sub(r'[^\x00-\x7F]+', '', input_string)
    # Remove unwanted symbols (keeping letters, numbers, spaces, and basic punctuation)
    sanitized_string = re.sub(r'[^a-zA-Z0-9\s.,!?\'\"-]', '', sanitized_string)
    return sanitized_string.strip()
