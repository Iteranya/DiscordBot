import process.charutil as charutil
import process.multimodal as multimodal

import config
import discord
import util
from process import promptutil
from process import history
from typing import Any

async def get_image_message_queue_item(message):
    image_description = await multimodal.read_image(message)
    message.content = f"\n[System Note: User sent the following attachment: {image_description}]"
    queue_item = {
        "simple_message": message, 
        "content":message.content
    }

    #config.queue_to_send_message.put_nowait(queue_item)
    return queue_item

async def get_text_prompt_queue_item(message: discord.Message, json_card: dict[str, Any],context) -> None:
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
    #context = await history.get_channel_history(message.channel)
    #check everything
    try:
        prompt = await promptutil.create_text_prompt(
            user, 
            character_prompt, 
            json_card, 
            context, 
            config.text_api, 
            image_data,
            message
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
        return queue_item
    except Exception as e:
        print("Prompt Crafting Error")
        return None
# Design The Grammars Here~
## Honestly a Nightmare, so Nothing for now~
async def get_action_prompt_queue_item(context, thought, message, json_card) -> None:
    user:str = message.author.display_name
    user = user.replace(" ", "")
    image_data=None
    # Clean the user's message to make it easy to read
    user_input = util.clean_user_message(message.clean_content)
    character_prompt = await charutil.get_character_prompt(json_card)
    try:
        prompt = await promptutil.create_action_prompt(
            user, 
            character_prompt, 
            json_card, 
            context, 
            config.text_api, 
            image_data,
            message,
            thought
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
        return queue_item
    except Exception as e:
        print("Prompt Crafting Error")
        return None
