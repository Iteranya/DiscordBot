


import json
import discord

async def create_text_prompt(
    user: str,
    character: str,
    bot: str,
    history: str,
    text_api,
    image_data,
    message:discord.message
 ) -> str:
    jb = bot["instructions"]
    
    prompt = character + history + "\n[System Note:"+jb+ "]\n\n[Reply] " + bot["name"] + ": "

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

def create_action_prompt(message,json,thought):
    
    return