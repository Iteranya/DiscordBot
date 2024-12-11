import re

import discord

# Test getting message history
async def get_channel_history(channel, append: str | None = None, limit: int = 50):
    history = []

    if isinstance(channel,discord.channel.TextChannel):
        if append:
            history.append(append)
        async for message in channel.history(limit=limit):
            name = str(message.author.display_name)

            # Sanitize the name by removing spaces, special characters, and converting to lowercase
            sanitized_name = re.sub(r'[^\w]', '', name)
            
            content = re.sub(r'<@!?[0-9]+>', '', message.content)  # Remove user mentions
            if content.startswith("[System"):
                history.append(content.strip())
            elif content.startswith("//"):
                #do nothing
                pass
            elif content.startswith("^"):
                content = content.replace("^","")
                history.append(f"[Reply]{sanitized_name}: {content.strip()}[End]")
            else:
                # Add the pseudonym function here
                history.append(f"[Reply]{sanitized_name}: {content.strip()}[End]")

    elif isinstance(channel,discord.Thread):
        if append:
            history.append(append)
        async for message in channel.history(limit=limit):
            name = str(message.author.display_name)

            # Sanitize the name by removing spaces, special characters, and converting to lowercase
            sanitized_name = re.sub(r'[^\w]', '', name)
            
            content = re.sub(r'<@!?[0-9]+>', '', message.content)  # Remove user mentions
            if content.startswith("[System"):
                history.append(content.strip())
            elif content=="[RESET]":
                history.append(content.strip())
            elif content.startswith("//"):
                #do nothing
                pass
            elif content.startswith("^"):
                content = content.replace("^","")
                history.append(f"[Reply]{sanitized_name}: {content.strip()}[End]")
            else:
                # Add the pseudonym function here
                history.append(f"[Reply]{sanitized_name}: {content.strip()}[End]")
            
    # Reverse the order of the collected messages
    history.reverse()
    contents = "\n\n".join(history)
    contents = reset_from_start(contents)
    contents += "\n\n"
    return contents

def reset_from_start(history: str) -> str:
    # Find the last occurrence of "[RESET]"
    last_reset = history.rfind("[RESET]")
    # If found, return everything after "[RESET]"
    if last_reset != -1:
        return history[last_reset + len("[RESET]"):].strip()
    # If not found, return the input string as is
    return history.strip()
