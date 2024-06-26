import re

# Test getting message history
async def get_channel_history(channel):
    history = []
    async for message in channel.history(limit=20):
        name = str(message.author.display_name)

        # Sanitize the name by removing spaces, special characters, and converting to lowercase
        sanitized_name = re.sub(r'[^\w]', '', name)

        content = re.sub(r'<@!?[0-9]+>', '', message.content)  # Remove user mentions
        history.append(f"{sanitized_name}: {content.strip()}")

    # Reverse the order of the collected messages
    history.reverse()
    contents = "\n".join(history)

    return contents
