import os
import re
import process.charutil as charutil
import process.multimodal as multimodal

import config
import discord
import util
from io import BytesIO
import io
import json
from PIL import Image
from PIL import Image
from observer import function
from process import history
from typing import Any
# This part decides what to do with the incoming message
# Also LAM stuff~(coming soon)

async def think(message: discord.Message, bot: str, reply: str) -> None:
    try:
        await message.add_reaction('✨')
    except Exception as e:
        print(e)
    json_card = await charutil.get_card(bot)

    if json_card is None:
        return
    
    if message.attachments:
        if(config.florence):
            image_description = await image_process(message)
        await convo(message,json_card,reply, image_description)
    else:
        await convo(message, json_card, reply, None)
        return

async def image_process(message):
    image_description = await multimodal.read_image(message)
    message.content = f"\n[System Note: User sent the following attachment: {image_description}]"
    queue_item = {
        "simple_message": message, 
    }

    config.queue_to_send_message.put_nowait(queue_item)
    return image_description

# TODO Add the Multimodal Thingy so you can send your waifu MEEEEMMMSSSSS!!!!
async def convo(message: discord.Message, json_card: dict[str, Any], reply: str, image_description) -> None:
    user:str = message.author.display_name
    user = user.replace(" ", "")

    if message.attachments:
        attachment = message.attachments[0]
        image_bytes = await attachment.read()
        #Toggle this to use just combine everything
        if attachment.filename.lower().endswith('.webp'):
            image_bytes = await util.convert_webp_bytes_to_png(image_bytes)
        base64_image = util.encode_image_to_base64(image_bytes)
        image_data = base64_image
    else:
        image_data=None

    # Clean the user's message to make it easy to read
    user_input = util.clean_user_message(message.clean_content)
    character_prompt = await charutil.get_character_prompt(json_card)
    context = await history.get_channel_history(message.channel)
    #check everything

    if (isinstance(user_input, str) and
        isinstance(user, str) and
        isinstance(character_prompt, str) and
        isinstance(json_card, dict) and
        isinstance(config.text_api, dict)):


        prompt = await create_text_prompt(
            user_input, 
            user, 
            character_prompt, 
            json_card, 
            context, 
            reply, 
            config.text_api, 
            image_description, 
            image_data
            )
        
        queue_item = {
            'prompt': prompt,
            'message': message,
            'user_input': user_input,
            'user': user,
            'image': None,
            'channel': None,
            'character':json_card
        }

        config.queue_to_process_message.put_nowait(queue_item)
    else:
        print("Something Went Wrong~")
        print(user_input)
        print(user)
        print(character_prompt)
        print(json_card)
        print(config.text_api)
    return

async def instagram_picuki_extras(message: discord.Message, reply) -> None:
    text = message
    text.content = text.content.replace('instagram.com', 'picuki.me')

    queue_item = {
        "simple_message": text, 
    }

    config.queue_to_send_message.put_nowait(queue_item)
    return

# TODO: Put the function below somewhere else
async def create_text_prompt(
    user_input: str,
    user: str,
    character: str,
    bot: str,
    history: str,
    reply: str,
    text_api: dict[str, Any],
    image_description,
    image_data
 ) -> str:
    jb = bot["instructions"]
    
    prompt = character + history +jb+ "\n\n[Reply] " + bot["name"] + ": "

    stopping_strings = ["[System", "[SYSTEM", "(System","(SYSTEM", user + ":", bot["name"] +
                        ":", "[Reply", "[REPLY"] 
    
    stopping_strings = set(stopping_strings)
    stopping_strings = list(stopping_strings)
    data = text_api["parameters"]
    
    data.update({"prompt": prompt})
    data.update({"stop_sequence": stopping_strings})
    if image_data:
        data.update({"images":[image_data]})
    
    data_string = json.dumps(data)
    data.update({"images": []})
    return data_string
