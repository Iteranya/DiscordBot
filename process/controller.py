import asyncio
import os
import re
import process.charutil as charutil
import process.multimodal as multimodal
from model import apiconfig
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
import lam
# This part decides what to do with the incoming message
# Also LAM stuff~(coming soon)

async def think() -> None:

    while True:
        content = await config.queue_to_process_everything.get()
        message = content["message"]
        bot = content["bot"]
        try:
            await message.add_reaction('✨')
        except Exception as e:
            print(e)

        json_card = await charutil.get_card(bot)
        message_content = message.content

        if json_card is None:
            pass
        
        if message_content.startswith("inst:"):
            await send_lam_message(message,json_card)
           

        if message.attachments:
            if(config.florence):
                await send_multimodal_message(message,json_card)
            else:
                await send_llm_message(message, json_card)
                
        else:
            await send_llm_message(message, json_card)
        config.queue_to_process_everything.task_done()

async def send_multimodal_message(message:discord.message, json_card):
    print("Multimodal Processing...")
    image_sys_message = await qutil.get_image_message_queue_item(message)
    await apiconfig.send_to_discord(image_sys_message)
    context = await history.get_channel_history(message.channel)
    text_bot_prompt = await qutil.get_text_prompt_queue_item(message,json_card,context)
    llm_response = await apiconfig.send_to_model_queue(text_bot_prompt)
    await apiconfig.send_to_discord(llm_response)
    return


async def send_llm_message(message,json_card):
    print("Chat Completion Processing...")
    context = await history.get_channel_history(message.channel)
    text_bot_prompt = await qutil.get_text_prompt_queue_item(message,json_card,context)
    llm_response = await apiconfig.send_to_model_queue(text_bot_prompt)
    await apiconfig.send_to_discord(llm_response)
    return


async def send_lam_message(message, json_card):
    print("LAM Processing...")
    context = await history.get_channel_history(message.channel)
    text_bot_prompt = await qutil.get_text_prompt_queue_item(message,json_card,context)
    llm_response = await apiconfig.send_to_model_queue(text_bot_prompt)

    thoughts = llm_response["response"]
    action_bot_prompt = await qutil.get_action_prompt_queue_item(context, thoughts, message, json_card)
    lam_response = await apiconfig.send_to_model_queue(action_bot_prompt)
    lam.process_action(lam_response)

    return