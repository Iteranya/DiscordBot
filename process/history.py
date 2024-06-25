import util
import os
import json
import discord
import re

# async def get_conversation_history(user, lines):

#     user = util.clean_username(user)
#     file = util.get_file_name("context", user + ".txt")

#     # Get as many lines from the file as needed
#     contents, length = await get_txt_file(file, lines)

#     if contents is None:
#         contents = ""

#     if length > 100:
#         await prune_text_file(file, 30)

#     return contents

# # Oh my god, this shit is as naive as a schoolgirl in a corruption doujin!!!
# async def add_to_conversation_history(message, user, file):

#     file = util.clean_username(file)
#     user = util.clean_username(user)
#     file_name = util.get_file_name("context", file + ".txt")

#     content = user + ": " + message + "\n"

#     await append_text_file(file_name, content)

# # Read in however many lines of a text file (for context or other text)
# # Returns a string with the contents of the file


# async def get_txt_file(filename, lines):

#     # Attempt to read the file and put its contents into a variable
#     try:
#         with open(filename, "r", encoding="utf-8") as file:  # Open the file in read mode
#             contents = file.readlines()
#             length = len(contents)
#             contents = contents[-lines:]

#             # Turn contents into a string for easier consumption
#             # I may not want to do this step. We'll see
#             history_string = ''.join(contents)

#             return history_string, length

#     # Let someone know if the file isn't where we expected to find it.
#     except FileNotFoundError:
#         await util.write_to_log("File " + filename + " not found. Where did you lose it?")
#         return None, 0

#     # Panic if we have no idea what's going in here
#     except Exception as e:
#         await util.write_to_log("An unexpected error occurred: " + e)
#         return None, 0


# async def prune_text_file(file, trim_to):

#     try:
#         with open(file, "r", encoding="utf-8") as f:  # Open the file in read mode
#             contents = f.readlines()
#             contents = contents[-trim_to:]  # Keep the last 'trim_to' lines

#         with open(file, "w", encoding="utf-8") as f:  # Open the file in write mode
#             f.writelines(contents)  # Write the pruned lines to the file

#     except FileNotFoundError:
#         await util.write_to_log("Could not prune file " + file + " because it doesn't exist.")

# # Append text to the end of a text file


# async def append_text_file(file, text):

#     with open(file, 'a+', encoding="utf-8") as context:
#         context.write(text)
#         context.close()


# Test getting message history
async def get_channel_history(channel: discord.TextChannel):
    history = []
    async for message in channel.history(limit=10):
        name = str(message.author.display_name)

        # Sanitize the name by removing spaces, special characters, and converting to lowercase
        sanitized_name = re.sub(r'[^\w]', '', name)

        content = re.sub(r'<@!?[0-9]+>', '', message.content)  # Remove user mentions
        history.append(f"{sanitized_name}: {content.strip()}")

    # Reverse the order of the collected messages
    history.reverse()
    contents = "\n".join(history)

    return contents