import requests
import json
import os
import discord
import re
from aiohttp import ClientSession
from aiohttp import ClientTimeout
from aiohttp import TCPConnector

from aiohttp import ClientSession
from aiohttp import ClientTimeout
from aiohttp import TCPConnector

from typing import Any

import config
import util
from model import llmresponse
from process import controller

# So in here, we get the model and immediately send the message
# TODO: Separate the sending part for a little bit of modularity

async def send_to_model_queue(content) -> None:
    # Get the queue item that's next in the list
    timeout = ClientTimeout(total=600)
    connector = TCPConnector(limit_per_host=10)
    async with ClientSession(timeout=timeout, connector=connector) as session:
        try:
            async with session.post(config.text_api["address"] + config.text_api["generation"], headers=config.text_api["headers"], data=content["prompt"]) as response:
                if response.status == 200:
                    try:
                        json_response = await response.json()
                        print("Json Responsse Get")
                        return await llmresponse.handle_llm_response(content, json_response)
                    except json.decoder.JSONDecodeError as e:
                        # Handle the case where response is not JSON-formatted
                        await handle_error_response(content, e)
                else:
                    # Handle non-200 responses here
                    print(f"HTTP request failed with status: {response.status}")

        except Exception as e:
            # Handle any other exceptions
            await handle_error_response(content, e)

async def handle_error_response(content: dict[str, Any], e: Exception) -> None:
    content["message"].content = "Bot's asleep, probably~ \nHere's the error code:" +str(e)
    queue_item={
        "text_message": content
    }
    await send_to_discord(queue_item)
    return None
# Alright, Time To Split This Fucker...
default_character_url = "https://i.imgur.com/mxlcovm.png"
default_character_name = config.bot_display_name


async def send_to_discord(llmreply) -> None:
    # Grab the reply that will be sent
        # Update reactions
    if llmreply is None:
        return
    try:
        await llmreply["content"]["message"].add_reaction('✅')
    except Exception as e:
        print("Hi!")

    if "simple_message" in llmreply:
        await send_as_user(llmreply)            
    elif "text_message" in llmreply:
        await send_as_sytem(llmreply)
    else:
        await send_as_bot(llmreply)


async def send_as_bot(llmreply):
    response = llmreply["response"]
    response = clean_text(response)
    response_chunks = [response[i:i+1500] for i in range(0, len(response), 1500)]

    character_name = llmreply["content"]["character"]["name"]  # Placeholder for character name
    character_avatar_url = llmreply["content"]["character"]["image"]  # Placeholder for character avatar URL
    
    for chunk in response_chunks:
        await send_webhook_message(llmreply["content"]["message"].channel, chunk, character_avatar_url, character_name)

async def send_as_user(llmreply):
    await send_webhook_message(llmreply["simple_message"].channel, llmreply["simple_message"].content, llmreply["simple_message"].author.avatar.url, llmreply["simple_message"].author.display_name)

async def send_as_sytem(llmreply):
    await send_webhook_message(llmreply["text_message"]["message"].channel, llmreply["text_message"]["message"].content,default_character_url, default_character_name)

  # Function to send messages using a webhook
async def send_webhook_message(channel: discord.TextChannel, content: str, avatar_url: str, username: str) -> None:
    if isinstance(channel, discord.DMChannel):
        return
    webhook_list = await channel.webhooks()
    # content = clean_text(content)

    for webhook in webhook_list:
        if webhook.name == "AktivaAI":
            await webhook.send(content, username=username, avatar_url=avatar_url)
            return

    webhook = await channel.create_webhook(name="AktivaAI")
    await webhook.send(content, username=username, avatar_url=avatar_url)




## TODO: Put these somewhere else

def clean_emojis(text):
    """
    Remove emojis from a given string.
    
    Args:
        text (str): Input string that may contain emojis
    
    Returns:
        str: String with emojis removed
    """
    # Regex pattern to match most emoji characters
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        "]+", flags=re.UNICODE)
    
    return emoji_pattern.sub(r'', text)

def clean_text(text):
    """
    Remove emojis, trailing whitespace, line breaks, and bracket-like characters from a given string.
    
    Args:
        text (str): Input string that may contain emojis, whitespace, line breaks, and trailing characters
    
    Returns:
        str: Cleaned string 
    """
    # Emoji pattern
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    
    # Remove trailing whitespace and line breaks first
    text = text.rstrip()
    
    # Remove emojis
    text_without_emoji = emoji_pattern.sub(r'', text)
    
    # Remove trailing bracket-like characters, with more inclusive matching
    cleaned_text = re.sub(r'[)\]>:;,\s]+$', '', text_without_emoji)
    
    return cleaned_text.rstrip()



async def set_api(config_file: str) -> dict[str, Any]:
    # Go grab the configuration file for me
    file = util.get_file_name("configurations", config_file)
    contents = await util.get_json_file(file)
    # If contents aren't none, clear the API and shove new data in
    api = {}

    if contents:
        api.update(contents)

    # Return the API
    return api

# Check to see if the API is running (pick any API)
async def api_status_check(link: str, headers):

    try:
        response = requests.get(link, headers=headers)
        status = response.ok
    except requests.exceptions.RequestException as e:
        print("Error occurred Language model not currently running.")
        status = False

    return status
