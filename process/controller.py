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
    await message.add_reaction('✨')
    json_card = await charutil.get_card(bot)

    if json_card is None:
        return

    # If user wants action
    if str(message.content).startswith("Instruction:"):
        await action(message, json_card, reply)
    # If user wants convo
    else:
        await convo(message, json_card, reply)

    return

# TODO Add the Multimodal Thingy so you can send your waifu MEEEEMMMSSSSS!!!!
async def convo(message: discord.Message, json_card: dict[str, Any], reply: str) -> None:
    user:str = message.author.display_name
    user = user.replace(" ", "")

    image_description = await multimodal.read_image(message)

    if message.attachments:
        attachment = message.attachments[0]
        image_bytes = await attachment.read()
        #Toggle this to use just combine everything
        image = Image.open(BytesIO(image_bytes))
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


        prompt = await create_text_prompt(user_input, user, character_prompt, json_card['name'], context, reply, config.text_api, image_description, image_data)
        
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

# async def action(message: discord.Message, client: discord.Client, bot: str):
async def action(message: discord.Message, json_card: dict[str, Any], reply: str):
    # WIP
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

    name_variations = await generate_name_variations(history)
    # The use JB is for a very niche use case, I will not recommend it.
    # If you make the character definition properly, this won't be a problem
    jb = "[System Note: The following reply will be written in 4 paragraphs or less without additional metacommentary]\n"
    if not image_data:
        image_prompt = ""
    elif image_description:
        image_prompt = "\n[System Note: Here's the Text Recognition Result from the Given Image:" + image_description + "]"
    else:
        image_prompt = f"\n[System Note: {user} sent an image attachment]"
    
    prompt = character + history + reply + user + \
        ": " + user_input + image_prompt + "\n" + bot + ": "

    stopping_strings = ["\n" + user + ":","[System", "[SYSTEM", user + ":", bot +
                        ":", "You:", "<|endoftext|>", "<|eot_id|>", "\nuser"] + name_variations
    
    print(stopping_strings)
    data = text_api["parameters"]
    
    data.update({"prompt": prompt})
    data.update({"stop_sequence": stopping_strings})
    if image_data:
        data.update({"images":[image_data]})
    
    data_string = json.dumps(data)
    data.update({"images": []})
    return data_string

def add_colon_to_string(string):
    return string + ':'

def process_names(names):
    processed_names = set()
    for name in names:
        processed_names.add(add_colon_to_string(name))
        processed_names.add(add_colon_to_string(name.lower()))
    return processed_names

async def generate_name_variations(history):
    user_list = function.get_user_list(history)
    bot_list = await function.get_bot_list()

    combined_list = set(user_list + bot_list)
    name_variations = process_names(combined_list)

    return list(name_variations)

# Call the function and store the result in a variable

