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
from process import lam
from duckduckgo_search import AsyncDDGS
# This part decides what to do with the incoming message
# Also LAM stuff~(coming soon)
import traceback
inline_comprehension = True
async def think() -> None:

    while True:
        content = await config.queue_to_process_everything.get()
        message:discord.message.Message = content["message"]
        bot = content["bot"]
        if isinstance(message.channel, discord.DMChannel):
            continue
        elif isinstance(message.channel,discord.Thread):
            channel_name = message.channel.name
            dimension = createOrFetchJson(sanitize_string(channel_name))
            try:
                
                await message.add_reaction('✨')
            except Exception as e:
                print(e)

            json_card = await charutil.get_card(bot)
            message_content = message.content # This is the string message
            
            if json_card is None:
                pass
            
            if message_content.startswith(">"):
                await send_lam_message(message,json_card)
            elif message_content.startswith("//"):
                pass
            elif message_content.startswith("^"):
                message_content = message_content.replace("^","")
                message_content = message_content.replace(str(json_card["name"]),"")
                message_content = message_content.strip()
                image_result =""
                message_content = extract_between_quotes(message_content)
                if "news" in message.content:
                    top_result = await get_news(message_content)
                elif "image" in message.content or "picture" in message.content:
                    image_result = await get_image(message_content)
                else:
                    top_result = await get_top_search_result(message_content)
                await send_grounded_message(message,json_card,dimension,str(top_result),image_result)
            elif message.attachments:
                if(config.florence):
                    await send_multimodal_message(message,json_card,dimension)
                else:
                    await send_llm_message(message, json_card,dimension)
            else:
                await send_llm_message(message, json_card,dimension)
            config.queue_to_process_everything.task_done()
        elif isinstance(message.channel,discord.channel.TextChannel):
            channel_name = message.channel.name
            dimension = createOrFetchJson(sanitize_string(channel_name))
            try:
                
                await message.add_reaction('✨')
            except Exception as e:
                print(e)

            json_card = await charutil.get_card(bot)
            message_content = message.content # This is the string message
            
            if json_card is None:
                pass
            
            if message_content.startswith(">"):
                await send_lam_message(message,json_card)
            elif message_content.startswith("//"):
                pass
            elif message_content.startswith("^"):
                message_content = message_content.replace("^","")
                message_content = message_content.replace(str(json_card["name"]),"")
                message_content = message_content.strip()
                image_result =""
                top_result = ""
                message_content = extract_between_quotes(message_content)
                if "news" in message.content:
                    top_result = await get_news(message_content)
                elif "image" in message.content or "picture" in message.content:
                    image_result = await get_image(message_content)
                else:
                    top_result = await get_top_search_result(message_content)
                await send_grounded_message(message,json_card,dimension,str(top_result),image_result)
            elif message.attachments:
                if(config.florence):
                    await send_multimodal_message(message,json_card,dimension)
                else:
                    await send_llm_message(message, json_card,dimension)
            else:
                await send_llm_message(message, json_card,dimension)
            config.queue_to_process_everything.task_done()

async def send_multimodal_message(message:discord.message, json_card,dimension):
    print("Multimodal Processing...")
    image_sys_message = await qutil.get_image_message_queue_item(message)
    context = await history.get_channel_history(message.channel)
    if inline_comprehension:
        context+="\n"+str(image_sys_message["content"])
    else:
        await apiconfig.send_to_discord(image_sys_message)
    
    text_bot_prompt = await qutil.get_text_prompt_queue_item(message,json_card,context,dimension)
    llm_response = await apiconfig.send_to_model_queue(text_bot_prompt)
    await apiconfig.send_to_discord(llm_response)
    return

async def send_grounded_message(message:discord.message, json_card,dimension,top_message,images=""):
    print("Grounding Processing...")
    
    context = await history.get_channel_history(message.channel)
    context+="\n[System Note: Web Search result: "+top_message+"]"
    text_bot_prompt = await qutil.get_text_prompt_queue_item(message,json_card,context,dimension)
    llm_response = await apiconfig.send_to_model_queue(text_bot_prompt)
    llm_response['response']+=images
    await apiconfig.send_to_discord(llm_response)
    return

async def send_llm_message(message,json_card,dimension):
    print("Chat Completion Processing...")
    context = await history.get_channel_history(message.channel)
    text_bot_prompt = await qutil.get_text_prompt_queue_item(message,json_card,context,dimension)
    llm_response = await apiconfig.send_to_model_queue(text_bot_prompt)
    await apiconfig.send_to_discord(llm_response)
    return

async def send_lam_message(message, json_card):
    print("LAM Processing...")
    context = await history.get_channel_history(message.channel)
    thoughts = "Alright then..."
    action_bot_prompt = await qutil.get_action_prompt_queue_item(context, thoughts, message, json_card)
    lam_response = await apiconfig.send_to_model_queue(action_bot_prompt)
    await lam.process_action(lam_response, message)

    return

async def send_positional_message(message:str,dimension):
    print("Positional Processing...")
    if message.startswith("^get"):
        await apiconfig.send_to_discord({
                "response":dimension["description"]
            })
    elif message.startswith("^set"):
        dimension["description"] = message
        replaceJsonContent(dimension["name"], dimension)
    else:
        pass  
    return

def createOrFetchJson(input_string):
    # File name with .json extension
    file_name = f"channels/{input_string}.json"

    # Check if the file already exists
    if os.path.exists(file_name):
        # Open and fetch the content
        with open(file_name, "r") as json_file:
            data = json.load(json_file)
        print(f"File '{file_name}' already exists. Fetched content: {data}")
        return data
    
    # If it doesn't exist, create the data and save it
    data = {
        "name": input_string,
        "description":"[System Note: Takes place in a discord text channel]",
        "global":"[System Note: Takes place in a discord server]",
        "instruction":"[System Note: Takes place in a discord text channel]"
        }
    with open(file_name, "w") as json_file:
        json.dump(data, json_file, indent=4)
    print(f"File '{file_name}' created with content: {data}")
    return data

def replaceJsonContent(file_name, new_content):
    """Replaces the content of the JSON file with a given dictionary."""
    # Ensure the file name ends with .json
    if not file_name.endswith(".json"):
        file_name += ".json"
    
    # Check if the file exists
    if not os.path.exists("channels/"+file_name):
        print(f"File '{file_name}' does not exist. Cannot replace content.")
        return None

    # Ensure new_content is a dictionary
    if not isinstance(new_content, dict):
        raise ValueError("New content must be a dictionary.")

    # Replace the content
    with open("channels/"+file_name, "w") as json_file:
        json.dump(new_content, json_file, indent=4)
    print(f"File '{file_name}' content replaced with: {new_content}")
    return new_content

def sanitize_string(input_string):

    sanitized_string = re.sub(r'[^\x00-\x7F]+', '', input_string)
    # Remove unwanted symbols (keeping letters, numbers, spaces, and basic punctuation)
    sanitized_string = re.sub(r'[^a-zA-Z0-9\s.,!?\'\"-]', '', sanitized_string)
    return sanitized_string.strip()

async def get_top_search_result(query: str, max_results: int = 5) -> dict:
    try:
        # Perform the search using AsyncDDGS
        results = await AsyncDDGS(verify= False).atext(
            query, 
            region='wt-wt',  # worldwide search
            safesearch="off",
            max_results=max_results
            
        )
        
        # Return the first result if available
        return results
    
    except Exception as e:
        traceback.print_exc()
        print(f"An error occurred during search: {e}")
        return {}

async def get_news(query: str, max_results: int = 5) -> dict:
    try:
        # Perform the search using AsyncDDGS
        results = await AsyncDDGS(verify= False).anews(
            query, 
            region='wt-wt',  # worldwide search
            safesearch="off",
            max_results=max_results
            
        )
        return results
    
    except Exception as e:
        traceback.print_exc()
        print(f"An error occurred during search: {e}")
        return {}

async def get_image(query: str, max_results: int = 5) -> dict:
    
    try:
        # Perform the search using AsyncDDGS
        results = await AsyncDDGS(verify= False).aimages(
            query, 
            region='wt-wt',  # worldwide search
            safesearch='off',
            max_results=max_results
        )
        
        # Return the first result if available
        return extract_image_links(results)
    
    except Exception as e:
        traceback.print_exc()
        print(f"An error occurred during search: {e}")
        return {}

def extract_image_links(results):
    # Extract the 'image' URLs from each dictionary in the results list
    links = [result['image'] for result in results if 'image' in result]

    # Join the links with newline characters
    return "\n".join(links)

def extract_between_quotes(input_string):
    import re
    match = re.search(r"\((.*?)\)", input_string)
    return match.group(1) if match else input_string
