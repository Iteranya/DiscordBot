import datetime
import re
import process.controller
from observer import function
import discord

# This is the main code that deals with determining what type of request is being given.
## Also the gateway to LAM

async def bot_behavior(message:discord.Message, client:discord.Client):

    reply = await function.get_reply(message, client)
    replied = function.get_replied_user(reply)
    print("Mark 1")
    #TODO: Specifically work that janky ass replied[0] thing

    #If bot's were being replied
    if reply is not None and replied:
        print("Mark 2")
        botlist = ["Ambruk-chan","Mecanica"] # Obviously we're not Hard Coding this, fucktard!
        for bot in list(botlist):
            print("Marks")
            print(replied[0])
            print(bot)
            if str(replied[0])==bot:
                print("Mark 3")
                await bot_think(message, bot.lower(), reply)
                return True

    #TODO: This part is where there will be fuzzy logic if more than one character is mentioned. But that will come way later.
    # If bot's name is mentioned
    if message.webhook_id is None:
        lower_text = message.content.lower()
        botlist = ["Ambruk-chan","Mecanica"] # Same here!

        # Check for each word in the list if it is present in the text
        for bot in botlist:
            if re.search(bot.lower(), lower_text):
                await bot_think(message, bot.lower(), reply)
                return True
        return False

    # Yes, no ping or DM, totally a feature, not a bug at all!!!

    # # If the bot is pinged
    # if client.user.mentioned_in(message):
    #     await bot_think(message, client)
    #     return True

    # # If someone DMs the bot, reply to them in the same DM
    # if message.guild is None and not message.author.bot:
    #     await bot_think(message, client)
    #     return True

    return False

async def bot_think(message:discord.Message, bot:str, reply:str):
    await process.controller.think(message,bot, reply)
    return