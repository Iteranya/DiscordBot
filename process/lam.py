import random
import re
from typing import Any

import discord

#Content:

async def process_action(content, message: discord.Message) -> None:
    command = content["response"]
    if re.search("<Debug Command>", command):
        print("LAM Triggered: <Debug Command>")
        await message.channel.send(f"Debug Commmand! How... very interesting...")
        return
    
    if re.search("<Get Profile Picture>", command):
        user = message.author
        avatar_url = user.display_avatar.url
        content["response"] = f"{user.name}'s profile picture:{avatar_url}"
        await send_as_bot(content)
        print("LAM Triggered: <Get Profile Picture>")
        return
    
    if re.search("<Roll Dice:", command):
        number = int(extract_number(command) or 0)
        if number > 0:
            results = [random.randint(1, 6) for _ in range(number)]
            content["response"] = f"🎲 You rolled: {', '.join(map(str, results))}"
            await send_as_bot(content)
        else:
            content["response"] = "Dropped the dice, try again"
            await send_as_bot(content)
        return
    
    if re.search("<Fortune Cookie>", command):
        fortunes = [
            "A pleasant surprise is waiting for you.",
            "Your hard work will pay off soon.",
            "Adventure awaits you around the next corner.",
            "Your creativity will shine bright today.",
            "A smile is your passport into the hearts of others."
        ]
        content["response"] = random.choice(fortunes)
        await send_as_bot(content)
        return

def extract_number(text: str) -> str | None:
    match = re.search(r": (\d+)", text)  # Matches digits after ": "
    if match:
        return match.group(1)  # Return the captured group (the number)
    else:
        return None
  
async def send_as_bot(llmreply: dict[str, Any]):
    response = llmreply["response"]
    response_chunks = [response[i:i+1500] for i in range(0, len(response), 1500)]

    character_name = llmreply["content"]["character"]["name"]  # Placeholder for character name
    character_avatar_url = llmreply["content"]["character"]["image"]  # Placeholder for character avatar URL

    for chunk in response_chunks:
        await send_webhook_message(llmreply["content"]["message"].channel, chunk, character_avatar_url, character_name)

async def send_webhook_message(channel: discord.TextChannel, content: str, avatar_url: str, username: str) -> None:
    webhook_list = await channel.webhooks()

    for webhook in webhook_list:
        if webhook.name == "AktivaAI":
            await webhook.send(content, username=username, avatar_url=avatar_url)
            return

    webhook = await channel.create_webhook(name="AktivaAI")
    await webhook.send(content, username=username, avatar_url=avatar_url)
