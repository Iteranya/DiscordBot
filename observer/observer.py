import datetime
import re
import process.controller as controller
from observer import function
import discord

# This is the main code that deals with determining what type of request is being given.
## Also the gateway to LAM

async def bot_behavior(message:discord.Message, client:discord.Client):
    botlist = await function.get_bot_list()
    reply = await function.get_reply(message, client)
    replied = function.get_replied_user(reply)
    #TODO: Specifically work that janky ass replied[0] thing

    #If bot's were being replied
    if reply is not None and replied:
        #botlist = ["Ambruk-chan","Mecanica"] # This fucker here, I need a function to retrieve all bot name. It's all in the characters folder in a json file.
        for bot in list(botlist):
            if str(replied[0])==bot:
                await bot_think(message, bot.lower(), "")
                return True

    #TODO: This part is where there will be fuzzy logic if more than one character is mentioned. But that will come way later.
    # If bot's name is mentioned
    if message.webhook_id is None:
        text = message.content

        # Check if contains the word 'https://www.instagram.com'
        if re.search("https://www.instagram.com",str(text)):
            await bot_action(message,reply)
            return True

        # Check for each word in the list if it is present in the text
        for bot in botlist:
            if re.search(bot.lower(), text.lower()):
                await bot_think(message, bot.lower(), reply)
                return True
        
        return False

    return False

async def bot_think(message:discord.Message, bot:str, reply:str):
    await controller.think(message,bot, reply)
    return

async def bot_action(message:discord.Message,reply:str):
    await controller.extras(message, reply)
    return 