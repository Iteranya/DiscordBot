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
    
    reply = await process_pseudonym(user,user_input)
    name_variations = await generate_name_variations(history)
    extracted_pseudonym = extract_pseudonym(user_input)
    if extracted_pseudonym:
        reply = await process_pseudonym(user,extracted_pseudonym)

    # The use JB is for a very niche use case, I will not recommend it.
    # If you make the character definition properly, this won't be a problem
    jb = f"[System Note: The following reply will be written in a way that portrays {bot}'s character in RP format]\n"
    if not image_data:
        image_prompt = ""
    elif image_description:
        image_prompt = "\n[System Note: Here's the Text Recognition Result from the Given Image:" + image_description + "]\n"
    else:
        image_prompt = f"\n[System Note: {user} sent an image attachment]"
    
    prompt = character + history + image_prompt + "\n\n" + jb + bot + ": "

    stopping_strings = [ user + ":","[System","\n[System", "[SYSTEM", user + ":", bot +
                        ":", "You:", "<|endoftext|>", "<|eot_id|>", "\nuser"] + name_variations
    
    print(stopping_strings)
    stopping_strings = set(stopping_strings)
    stopping_strings = list(stopping_strings)
    print(reply)
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
        processed_names.add(f"{name.lower()}:")
        #processed_names.add(add_colon_to_string(name.lower()))
        processed_names.add(f"{name}:")

    return processed_names

async def generate_name_variations(history):
    user_list = function.get_user_list(history)
    bot_list = await function.get_bot_list()
    pseudonym_list = get_keys_from_json()
    if(pseudonym_list):
        combined_list = set(user_list + bot_list + pseudonym_list)
    else:
        combined_list = set(user_list + bot_list)
    name_variations = process_names(combined_list)

    return list(name_variations)

# Call the function and store the result in a variable

async def process_pseudonym(user,extracted_pseudonym):
    name_mapping = json_to_string_map()
    result = ""
    # Check for specific keywords in the content to apply pseudonyms
    for key, pseudonym in name_mapping.items():
        if extracted_pseudonym[0] == key:
            result = f"{pseudonym}: {extracted_pseudonym[1]}"
            print("Pseudonym Found")
            return result
            
    result = f"{user}: {extracted_pseudonym[1]}"
    print("Pseudonym Not Found")
    return result

def json_to_string_map():
    json_file = "Pseudonym.json"
    try:
        root_path = os.path.dirname(os.path.abspath(__file__))  # Get the absolute path of the current script
        json_path = "Pseudonym.json"  # Construct the full path to the JSON file
        with open(json_path, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"Error: The file at {json_path} was not found.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: The file at {json_path} is not a valid JSON.")
        return {}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {}
    
def get_keys_from_json():
     try:
        json_path = "Pseudonym.json"  # Construct the full path to the JSON file
        with open(json_path, 'r') as file:
            data = json.load(file)
            string_list = [f"{value}" for value in data.values()]
            return string_list
     except FileNotFoundError:
         print("No Pseudonym.json found in the root")

def extract_pseudonym(input_string):

    # Define the regex pattern to match "user" and "Says something"
    pattern = r"^(\w+):\s(.+)$"

    # Use re.match to find the pattern in the string
    match = re.match(pattern, input_string)

    if match:
        user = match.group(1)  # This will be "user"
        message = match.group(2)  # This will be "Says something"
        return [user,message]
    else:
        return None
        