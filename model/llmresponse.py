import re
import util
from typing import Any

import config
from process import controller

# Let's separate the sending part of
async def handle_llm_response(content: str, response: dict[str, Any]) -> None:
    llm_response = response
    try:
        data = llm_response['results'][0]['text']
    except KeyError:
        data = llm_response['choices'][0]['message']['content']

    if not data:
        return
    cleaned_data:str = remove_last_word_before_final_colon(data)
    cleaned_data = remove_string_before_final(cleaned_data)
    cleaned_data = cleaned_data.strip()
    if cleaned_data.endswith("*"):
        cleaned_data  = remove_fluff(cleaned_data)
    llm_message = cleaned_data
    
    message = {
        "response": llm_message, 
        "content": content,
        }

    if not llm_message:
        await util.write_to_log("hm, llm_message is empty..")
        return None
    
    return message

    

def remove_last_word_before_final_colon(text: str) -> str:
    # Define the regex pattern to find the last word before the final colon
    pattern = r'\b\w+\s*:$'
    
    # Use re.sub to replace the matched pattern with an empty string
    result = re.sub(pattern, '', text)
    
    return result.strip()  # Remove any leading or trailing whitespace

def remove_string_before_final(data: str) -> str:
    substrings = ["[/","[System", "[SYSTEM", "[Reply", "[REPLY", "(System", "(SYSTEM","[End]"]
    
    for substr in substrings:
        if data.endswith(substr):
            return data[:-len(substr)]
    
    return data

def remove_fluff(text: str) -> str:
    # Find the last pair of asterisks and the content between them
    pattern = r'\*(.*?)\*'
    
    # Use re.findall to get all matches and re.sub to remove the last one
    matches = re.findall(pattern, text)
    if matches:
        # Get the last match and construct the regex to remove it
        last_fluff = re.escape(f"*{matches[-1]}*")
        text = re.sub(last_fluff, '', text, count=1)
    
    return text.strip()  # Remove any extra whitespace
