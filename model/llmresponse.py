import re
import util
from typing import Any

import config

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
    llm_message = cleaned_data
    
    queue_item = {
        "response": llm_message, 
        "content": content,
        }

    if not llm_message:
        await util.write_to_log("hm, llm_message is empty..")
        return

    await util.write_to_log("LLM response is: " + llm_message)

    config.queue_to_send_message.put_nowait(queue_item)

def remove_last_word_before_final_colon(text: str) -> str:
    # Define the regex pattern to find the last word before the final colon
    pattern = r'\b\w+\s*:$'
    
    # Use re.sub to replace the matched pattern with an empty string
    result = re.sub(pattern, '', text)
    
    return result.strip()  # Remove any leading or trailing whitespace

def remove_string_before_final(data: str) -> str:
    substrings = ["[System", "[SYSTEM", "[Reply", "[REPLY", "(System", "(SYSTEM"]
    
    for substr in substrings:
        if data.endswith(substr):
            return data[:-len(substr)]
    
    return data
