import requests
import json
import os
import discord

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
    webhook_list = await channel.webhooks()

    for webhook in webhook_list:
        if webhook.name == "AktivaAI":
            await webhook.send(content, username=username, avatar_url=avatar_url)
            return

    webhook = await channel.create_webhook(name="AktivaAI")
    await webhook.send(content, username=username, avatar_url=avatar_url)




## TODO: Put these somewhere else




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
