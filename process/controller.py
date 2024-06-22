# For xtts2 TTS (now imported conditionally at the bottom of the script)
# import torch
# import torchaudio
# from TTS.tts.configs.xtts_config import XttsConfig
# from TTS.tts.models.xtts import Xtts


import process.charutil as charutil
import process.multimodal as multimodal

import config
import discord
import util
from process import history
from observer import function
import json
# This part decides what to do with the incoming message
# Also LAM stuff~(coming soon)

async def think(message:discord.Message, bot:str, reply:str):
    await message.add_reaction('✨')
    json_card = await charutil.get_card(bot)

    # If user wants action
    if str(message.content).startswith("Instruction:"):
        await action(message,json_card,reply)

    # If user wants convo
    else:
        await convo(message,json_card, reply)
    return

# Welp, Time To Redo This Sonuvabitch
# ...
# Tomorrow...
# TODO
async def convo(message:discord.Message,json_card:dict[str,any],reply:str):
    user:str = message.author.display_name
    user = user.replace(" ", "")

    image_description = await multimodal.read_image(message)

    # Clean the user's message to make it easy to read
    user_input = util.clean_user_message(message.clean_content)
    character_prompt = await charutil.get_character_prompt(json_card)
    context = await history.get_conversation_history(user, 15)

    #check everything

    if (isinstance(user_input, str) and
        isinstance(user, str) and
        isinstance(character_prompt, str) and
        isinstance(json_card, dict) and
        isinstance(config.text_api, dict)):


        prompt = await create_text_prompt(user_input, user, character_prompt, json_card['name'], context, reply, config.text_api, None)
        
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

async def action(message,client,bot):
    # WIP
    return

async def create_text_prompt(user_input, user, character, bot, history, reply, text_api, image_description=None):

    if image_description:
        image_prompt = "[NOTE TO AI - USER MESSAGE CONTAINS AN IMAGE. IMAGE RECOGNITION HAS BEEN RUN ON THE IMAGE. DESCRIPTION OF THE IMAGE: " + \
            image_description.capitalize() + "]"
        prompt = character + history + reply + user + ": " + \
            user_input + "\n" + image_prompt + "\n" + bot + ": "
    else:
        eot = function.get_user_list(history)
        eot = add_colon_to_strings(eot)
        replied = function.get_replied_user(reply)
        replied = add_colon_to_strings(replied)
        prompt = character + history + reply + user + \
            ": " + user_input + "\n" + bot + ": "
    stopping_strings = ["\n" + user + ":", user + ":", bot +
                        ":", "You:", "@Ava", "User", "@" + user, "<|endoftext|>", "<|eot_id|>", "\nuser"] + eot + replied
    
    print(stopping_strings)
    data = text_api["parameters"]

    if text_api["name"] == "openai":
        messages = [
            {
                "role": "user",
                "content": prompt
            }
        ]
 #       data.update({"stop": stopping_strings})
        data.update({"messages": messages})
    else:
        data.update({"prompt": prompt})
        data.update({"stop_sequence": stopping_strings})

    data_string = json.dumps(data)
    return data_string

def add_colon_to_strings(string_list):
    # Create a new list to store modified strings
    modified_list = []
    
    # Iterate through each string in the input list
    for string in string_list:
        # Append the string with a colon at the end to the modified list
        modified_list.append(string + ':')
    
    return modified_list