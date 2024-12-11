import re
import process.controller as controller
from observer import function
import discord
from process import history
import config

# This is the main code that deals with determining what type of request is being given.
## Also the gateway to LAM

async def bot_behavior(message: discord.Message, client: discord.Client) -> bool:
    botlist = await function.get_bot_list()
    reply = await function.get_reply(message, client)
    replied = function.get_replied_user(reply)
    # TODO: Specifically work that janky ass replied[0] thing

    #If bot's were being replied
    if reply is not None and replied:
        for bot in list(botlist):
            if str(replied[0])==bot:
                await bot_think(message, bot.lower())
                return True
        
    #The Fuzzy Logic Part~
    if message.webhook_id is None:
        text = message.content
        # if message.channel.type == discord.ChannelType.public_thread or message.channel.type == discord.ChannelType.private_thread:
        #     return True

         # Check for each word in the list if it is present in the text
        for bot in botlist:
            if re.search(bot.lower(), text.lower()):
                await bot_think(message, bot.lower())
                return True

        # Check if contains the word 'Debugus Starticus!'
        if re.search("Debugus Starticus!", str(text)):
            print(await history.get_channel_history(message.channel))
            return True

        return False

    return False

async def bot_think(message: discord.Message, bot: str) -> None:
    queue_item = {
        "message" : message,
        "bot" : bot
    }
    config.queue_to_process_everything.put_nowait(queue_item)
    return
