import json
import discord

async def create_text_prompt(
    user: str,
    character: str,
    bot: str,
    history: str,
    text_api,
    image_data,
    message:discord.message,
    dimension
 ) -> str:
    jb = bot["instructions"]
    #jb = "" # Toggle this to disable JB
    prompt = character+dimension["global"] +history + dimension["description"] + jb+"\n[Reply]\n " + bot["name"] + ":"

    stopping_strings = ["[System", "(System", user + ":",  "[Reply", "(Reply", "System Note", "[End]","[/"] 
    
    stopping_strings = set(stopping_strings)
    stopping_strings = list(stopping_strings)
    data = text_api["parameters"]
    
    data.update({"prompt": prompt})
    data.update({"stop_sequence": stopping_strings})
    if image_data:
        data.update({"images":[image_data]})
    data.update({"grammar": ""})
    data.update({"grammar_string": ""})
    data.update({"grammars": ""})
    data_string = json.dumps(data)
    data.update({"images": []})
    
    return data_string

async def create_action_prompt(
    user: str,
    character: str,
    bot,
    history: str,
    text_api,
    image_data,
    message:discord.message,
    thought
 ) -> str:
    jb = bot["instructions"]
    
    prompt = character + history + bot["name"]+ ": " +thought + "\n[Action:"

    
    
    stopping_strings = ["[END]"]
    
    stopping_strings = set(stopping_strings)
    stopping_strings = list(stopping_strings)
    data = text_api["parameters"]

    # Hooo, boy, here we go...
    grammars = " root ::= \"[System Action: <\" command \">][END]\"\ncommand ::= (dice|\"Get Profile Picture\"|\"Fortune Cookie\"|\"Debug Command\")\ndice ::= \"Roll Dice: \" num+\nnum ::= (\"1\"|\"2\"|\"3\"|\"4\"|\"5\"|\"6\"|\"7\"|\"8\"|\"9\") "

    data.update({"prompt": prompt})
    data.update({"stop_sequence": stopping_strings})
    data.update({"grammar": grammars})
    data.update({"grammar_string": grammars})
    if image_data:
        data.update({"images":[image_data]})
    
    data_string = json.dumps(data)
    data.update({"images": []})
    return data_string
    