import json
import os
import discord
import config
from observer import function


client = config.client

class EditMessageModal(discord.ui.Modal, title='Edit Message'):
    def __init__(self, original_message):
        super().__init__()
        self.original_message = original_message

        # Set the default value of the TextInput to the content of the original message
        self.new_content = discord.ui.TextInput(
            label='New Content', 
            style=discord.TextStyle.long, 
            required=True, 
            default=self.original_message.content
        )
        # Add the TextInput to the modal
        self.add_item(self.new_content)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            await edit(self.original_message, self.new_content.value)
            await interaction.response.send_message("Message edited successfully!", ephemeral=True)
        except Exception:
            await interaction.response.send_message("This ain't my AI~", ephemeral=True)

    # async def on_submit(self, interaction: discord.Interaction):
    #     await edit(self.original_message, self.new_content.value)
    #     await interaction.response.send_message("Message edited successfully!", ephemeral=True)



async def delete_message_context(interaction: discord.Interaction, message: discord.Message):
    await interaction.response.send_message("Still a WIP, it doesn't delete it from memory", ephemeral=True)
    await delete(message)

async def edit_message_context(interaction: discord.Interaction, message: discord.Message):
    await client.fetch_webhook(message.webhook_id)
    await interaction.response.send_modal(EditMessageModal(message))

async def edit(message:discord.Message, new_content):
    webhook = await client.fetch_webhook(message.webhook_id)
    await webhook.edit_message(message_id=message.id,content=new_content)

async def delete(message:discord.Message):
    webhook = await client.fetch_webhook(message.webhook_id)
    await webhook.delete_message(message.id)

async def character_info():
    character = await get_bot()
    result_str = "\n".join([f"{name}: {info}" for name, info in character.items()])
    return result_str

async def get_bot():
    folder_path = "./characters"
    bot_dict = {}  # Dictionary to store bot name and info

    # Iterate over each file in the directory
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if filename.endswith('.json'):
            # Read the JSON file
            with open(file_path, 'r') as f:
                try:
                    # Load JSON data
                    data = json.load(f)
                    # Extract the name field and append to names list
                    name = data.get('name')
                    info = data.get('info')
                    if name and info:
                        # Put the bot name and info in a dictionary
                        bot_dict[name] = info
                except json.JSONDecodeError as e:
                    print(f"Error parsing {filename}: {e}")

    return bot_dict



# Well Fuck, I need to redo the memory first!!!