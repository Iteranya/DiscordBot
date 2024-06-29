# This is the Character Swapping Part

# This is the function that supports the Observer
import os
import json
from typing import Any

# For xtts2 TTS (now imported conditionally at the bottom of the script)
# import torch
# import torchaudio
# from TTS.tts.configs.xtts_config import XttsConfig
# from TTS.tts.models.xtts import Xtts

async def determineType():
    return 

# IT'S THIS PART!!!

async def get_card(bot_name: str):
    directory = "./characters"
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            filepath = os.path.join(directory, filename)
            try:
                # Open and load JSON file
                with open(filepath, 'r', encoding='utf-8') as file:
                    data = json.load(file)

                # Check if 'name' field matches target_name
                if "name" in data and str(data["name"]).lower() == str(bot_name).lower():
                    return data
            except json.JSONDecodeError:
                print(f"Error decoding JSON in file: {filepath}")
            except Exception as e:
                print(f"Error processing file {filepath}: {e}")

async def get_character_prompt(json_card: dict[str, Any] | None) -> str | None:
    if(json_card is None):  # FIXME: Mr Paradox seems to be having a skill issue moment here, kek
        print("IS NOT A VALID JSON IN LINE 46... WHY!?!?!?")
        return None
    else:
        # Your name is <name>.
        character: str = "You are " + json_card["name"] + ", you embody their character, persona, goals, personality, and bias which is described in detail below:"

        # Your name is <name>. You are a <persona>.
        character = character + "Your persona: " + json_card["persona"] + ". "

        # Instructions on what the bot should do. This is where an instruction model will get its stuff.

        examples = json_card["examples"]  # put example responses here

        for example in examples:
            if example.startswith("[System"):
                pass
            else:
                example = f"[Reply] {example}"

        # Example messages!
        character_prompt = character + " A history reference to your speaking quirks and behavior: " + \
        "\n" + '\n'.join(examples) + "\n"

        return character_prompt
