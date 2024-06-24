import asyncio
import os
import discord
from discord import app_commands
from discord import Intents
from discord import Client
import logging
import argparse
import config
from process import charutil

import util

from discord import app_commands
from dotenv import load_dotenv
from observer import observer
from model import apiconfig

client = config.client

class EditMessageModal(discord.ui.Modal, title='Edit Message'):
    new_content = discord.ui.TextInput(label="Still WIP", style=discord.TextStyle.long, required=True)

    def __init__(self, original_message):
        super().__init__()
        self.original_message = original_message

    async def on_submit(self, interaction: discord.Interaction):
        await edit(self.original_message,self.new_content.value)
        await interaction.response.send_message("This feature is WIP, doesn't really change the character's memory, unfortunately.", ephemeral=True)


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

# Well Fuck, I need to redo the memory first!!!