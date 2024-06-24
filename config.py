# config.py
import os
import discord
from dotenv import load_dotenv
import asyncio

load_dotenv()
global text_api
global image_api
global character_card
global tts_config, tts_model, gpt_cond_latent, speaker_embedding
discord_token:str = os.getenv("DISCORD_API_KEY")

# Other configurations
queue_to_process_message = asyncio.Queue()
queue_to_process_image = asyncio.Queue()
queue_to_send_message = asyncio.Queue()

tts_config = None
tts_model = None
gpt_cond_latent = None
speaker_embedding = None

text_api: dict = {}
image_api:dict = {}

# Dictionary to keep track of the bot's last message time and last mentioned channel by guild
bot_last_message_time = {}
bot_last_mentioned_channel = {}
intents: discord.Intents = discord.Intents.default()
intents.message_content = True
client:discord.Client = discord.Client(command_prefix='/', intents=intents)

