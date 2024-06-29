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

async def send_to_model_queue() -> None:

    while True:
        # Get the queue item that's next in the list
        content = await config.queue_to_process_message.get()
        await util.write_to_log("send_to_model_queue()")

        # Grab the data JSON we want to send it to the LLM
        if not content['channel']:
            await util.write_to_log("Sending prompt from " + content["user"] + " to LLM model.")
        else:
            await util.write_to_log("Sending prompt for " + content['channel'].name + " to LLM model.")
        await util.write_to_log("Prompt is: " + content["prompt"])

        timeout = ClientTimeout(total=600)
        connector = TCPConnector(limit_per_host=10)
        async with ClientSession(timeout=timeout, connector=connector) as session:
            try:
                async with session.post(config.text_api["address"] + config.text_api["generation"], headers=config.text_api["headers"], data=content["prompt"]) as response:
                    if response.status == 200:
                        try:
                            json_response = await response.json()
                            await llmresponse.handle_llm_response(content, json_response)
                        except json.decoder.JSONDecodeError as e:
                            # Handle the case where response is not JSON-formatted
                            print(f"Failed to decode JSON response: {e}")
                            text_response = await response.text()
                            print(f"Response text was: {text_response}")
                    else:
                        # Handle non-200 responses here
                        print(f"HTTP request failed with status: {response.status}")

                config.queue_to_process_message.task_done()
            except Exception as e:
                # Handle any other exceptions
                await handle_error_response(content, e)

async def handle_error_response(content: dict[str, Any], e: Exception) -> None:
    content["message"].content = "Bot's asleep, probably~ \nHere's the error code:" +str(e)
    queue_item={
        "text_message": content
    }
    config.queue_to_send_message.put_nowait(queue_item)


async def send_to_stable_diffusion_queue() -> None:
    global image_api  # FIXME: Unbound

    while True:
        image_prompt = await config.queue_to_process_image.get()

        data = image_api["parameters"]
        data["prompt"] = data["preprompt"] + image_prompt["response"]
        data_json = json.dumps(data)

        await util.write_to_log("Sending prompt from " + image_prompt["content"]["user"] + " to Stable Diffusion model.")
        await util.write_to_log("Prompt is: " + image_prompt["response"])
        await util.write_to_log("Json sent to SD is: " + data_json)

        try:
            async with ClientSession() as session:
                async with session.post(image_api["link"], headers=image_api["headers"], data=data_json) as response:
                    response = await response.read()
                    sd_response = json.loads(response)
                    if "images" not in sd_response:
                        await util.write_to_log("Stable Diffusion did not return a valid image. Ran out of VRAM perhaps?")
                    else:
                        image = util.image_from_string(
                            sd_response["images"][0])

                        queue_item = {
                            "response": image_prompt["response"],
                            "image": image,
                            "content": image_prompt["content"]
                        }
                        config.queue_to_send_message.put_nowait(queue_item)
        except Exception as e:
            await util.write_to_log("Connection to Stable Diffusion failed")

        config.queue_to_process_image.task_done()

async def send_to_discord_queue() -> None:
        while True:
            # Grab the reply that will be sent
            llmreply = await config.queue_to_send_message.get()

            default_character_url = "https://i.imgur.com/mxlcovm.png"
            default_character_name = config.bot_display_name

            if "simple_message" in llmreply:
                
                await send_webhook_message(llmreply["simple_message"].channel, llmreply["simple_message"].content, llmreply["simple_message"].author.avatar.url, llmreply["simple_message"].author.display_name)
                config.queue_to_send_message.task_done()
                #await llmreply["simple_message"].delete() #Comment this out to disable deleting part
            
            elif "text_message" in llmreply:
                await send_webhook_message(llmreply["text_message"]["message"].channel, llmreply["text_message"]["message"].content,default_character_url, default_character_name)
                config.queue_to_send_message.task_done()
            else:
                if not llmreply["content"]["channel"]:

                    # Update reactions
                    try:
                        await llmreply["content"]["message"].add_reaction('✅')
                    except Exception as e:
                        print("Hi!")

                # Split the response into chunks of 1500 characters
                response = llmreply["response"]
                response_chunks = [response[i:i+1500] for i in range(0, len(response), 1500)]

                character_name = llmreply["content"]["character"]["name"]  # Placeholder for character name
                character_avatar_url = llmreply["content"]["character"]["image"]  # Placeholder for character avatar URL

                if not llmreply["content"]["image"]:
                    if not llmreply["content"]["channel"]:
                        for chunk in response_chunks:
                            await send_webhook_message(llmreply["content"]["message"].channel, chunk, character_avatar_url, character_name)
                    # else:
                    #     # Send random message on channel
                    #     print("Sending random message.")
                    #     for chunk in response_chunks:
                    #         await send_webhook_message(llmreply["content"]["channel"], chunk, character_avatar_url, character_name)
                else:
                    image_file = discord.File(llmreply["image"])
                    # Since we need to send an image, we can't use webhooks directly to send files. Instead, we send the message first and then send the file.
                    if not llmreply["content"]["channel"]:
                        for chunk in response_chunks:
                            await send_webhook_message(llmreply["content"]["message"].channel, chunk, character_avatar_url, character_name)
                        await llmreply["content"]["message"].channel.send(llmreply["response"], file=image_file, reference=llmreply["content"]["message"])
                    else:
                        for chunk in response_chunks:
                            await send_webhook_message(llmreply["content"]["channel"], chunk, character_avatar_url, character_name)
                        await llmreply["content"]["channel"].send(llmreply["response"], file=image_file)

                    os.remove(llmreply["image"])

                config.queue_to_send_message.task_done()

  # Function to send messages using a webhook
async def send_webhook_message(channel: discord.TextChannel, content: str, avatar_url: str, username: str) -> None:
    webhook_list = await channel.webhooks()

    for webhook in webhook_list:
        if webhook.name == "AktivaAI":
            await webhook.send(content, username=username, avatar_url=avatar_url)
            return

    webhook = await channel.create_webhook(name="AktivaAI")
    await webhook.send(content, username=username, avatar_url=avatar_url)

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
