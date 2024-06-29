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
from process import qutil
from process import history
from typing import Any
# This part decides what to do with the incoming message
# Also LAM stuff~(coming soon)

async def think(message: discord.Message, bot: str) -> None:
    try:
        await message.add_reaction('✨')
    except Exception as e:
        print(e)
    json_card = await charutil.get_card(bot)
    message_content = message.content

    if json_card is None:
        return
    
    if message_content.startswith("inst:"):
        await send_lam_message(message,json_card)
        return
    if message.attachments:
        if(config.florence):
            await send_multimodal_message(message,json_card)
            return
        else:
            await send_llm_message
            return
    else:
        await send_llm_message(message, json_card)
        return

async def send_multimodal_message(message:discord.message, json_card):
    print("Multimodal Processing...")
    image_sys_message = await qutil.get_image_message_queue_item(message)
    config.queue_to_send_message.put_nowait(image_sys_message)
    append = str(image_sys_message["simple_message"].content)
    print(append)
    context = await history.get_channel_history(message.channel,append)
    text_bot_prompt = await qutil.get_text_prompt_queue_item(message,json_card,context)
    config.queue_to_process_message.put_nowait(text_bot_prompt)
    return

async def send_llm_message(message,json_card):
    print("Chat Completition Processing...")
    context = await history.get_channel_history(message.channel)
    text_bot_prompt = await qutil.get_text_prompt_queue_item(message,json_card,context)
    config.queue_to_process_message.put_nowait(text_bot_prompt)
    return

async def send_lam_message(message, json_card):
    print("LAM Processing...")
    context = await history.get_channel_history(message.channel)
    text_bot_prompt = await qutil.get_text_prompt_queue_item(message,json_card,context)
    config.queue_to_process_message.put_nowait(text_bot_prompt)
    action_bot_prompt = await qutil.get_action_prompt_queue_item(message,json_card)
    config.queue_to_process_message.put_nowait(action_bot_prompt)
    return

async def process_ai_message(response):
    # This is where we check if it contains LAM Commands or not
    print("Made it here~")
    content = str(response["response"])
    if content.startswith("[Next Action"):
        print("Processing LAM...")

    config.queue_to_send_message.put_nowait(response)
    return