import re

import discord

# Test getting message history
async def get_channel_history(channel: discord.abc.MessageableChannel, append: str | None = None, limit: int = 20):
    history = []
    if append:
        history.append(append)
    async for message in channel.history(limit=limit):
        name = str(message.author.display_name)

        # Sanitize the name by removing spaces, special characters, and converting to lowercase
        sanitized_name = re.sub(r'[^\w]', '', name)
        
        content = re.sub(r'<@!?[0-9]+>', '', message.content)  # Remove user mentions
        if content.startswith("[System"):
            history.append(content.strip())
        else:
            history.append(f"[Reply] {sanitized_name}: {content.strip()}")
        
    # Reverse the order of the collected messages
    history.reverse()
    contents = "\n\n".join(history)
    return contents
