# This is the Multi Modal Part
# For now this will only support Image Recognition, but later on who knows???
from io import BytesIO
import json
from PIL import Image
import pytesseract


# For xtts2 TTS (now imported conditionally at the bottom of the script)
# import torch
# import torchaudio
# from TTS.tts.configs.xtts_config import XttsConfig
# from TTS.tts.models.xtts import Xtts

from aiohttp import ClientSession

import util

# async def read_image(message):
#     try:
#         # Process each attachment (actually just one for now)
#         for attachment in message.attachments:
#             # Check if it is an image based on content type
#             if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']):
#                 # Download the image bytes
#                 # Uses the read method from discord.Attachment class
#                 image_bytes = await attachment.read()

#                 # if .webp -> convert to PNG for llava
#                 if attachment.filename.lower().endswith('.webp'):
#                     image_bytes = await util.convert_webp_bytes_to_png(image_bytes)

#                 # Convert the image to base64
#                 base64_image = util.encode_image_to_base64(image_bytes)

#                 # Define the POST data
#                 post_data = {
#                     'prompt': "USER: Describe what you see and recognize in this image: [img-1] \nASSISTANT: ",
#                     'n_predict': 256,
#                     'image_data': [{"data": base64_image, "id": 1}],
#                     'ignore_eos': False,
#                     'temperature': 0.1
#                 }

#                 # Encode the data as JSON
#                 json_data = json.dumps(post_data)

#                 # Set the request headers
#                 headers = {
#                     'Content-Type': 'application/json',
#                 }

#                 # Specify the URL
#                 llava_url = "http://localhost:8007/completion"

#                 # Perform the HTTP POST request for image analysis
#                 async with ClientSession() as session:
#                     async with session.post(llava_url, headers=headers, data=json_data) as response:
#                         if response.status == 200:
#                             response_data = await response.json()
#                             image_description = response_data['content']

#                             # Send the response back to the Discord channel
#                             # await message.channel.send(image_description, reference=message)
#                             return image_description
#                         else:
#                             # Handle unexpected status code
#                             errorstr = f"Error: The server responded with an unexpected status code: {response.status}"
#                             await util.write_to_log(errorstr)
#                             return None

#             else:
#                 # If no image is found
#                 await util.write_to_log("No supported image attachments found.")
#                 return None

#     except Exception as e:
#         # Handle any other exception that was not explicitly caught
#         error_msg = f"An error occurred: {str(e)}"
#         await util.write_to_log(error_msg)
#         return None
#     return None

async def read_image(message):
    try:
        # Process each attachment (actually just one for now)
        for attachment in message.attachments:
            # Check if it is an image based on content type
            if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']):
                image_bytes = await attachment.read()
                if attachment.filename.lower().endswith('.webp'):
                    image_bytes = await util.convert_webp_bytes_to_png(image_bytes)
                image_description = await process_image(image_bytes)
                return image_description
            else:
                # Check if it is a link to an image
                if attachment.url:
                    if any(attachment.url.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']):
                        # You would typically fetch the image from the URL here
                        # For example, using aiohttp to fetch the image
                        import aiohttp
                        async with aiohttp.ClientSession() as session:
                            async with session.get(attachment.url) as response:
                                if response.status == 200:
                                    image_bytes = await response.read()
                                    image_description = await process_image(image_bytes)
                                    return image_description
    except Exception as e:
        print(f"An error occurred: {e}")

async def process_image(image_bytes):
    try:
            
            image = Image.open(BytesIO(image_bytes))

            # OCR~
            recognized_text = pytesseract.image_to_string(image).strip()
            base64_image = util.encode_image_to_base64(image_bytes)

            # Process each attachment (actually just one for now)
            # Check if it is an image based on content type

            if not recognized_text:
                recognized_text = "No text recognized in the image."

            # Define the POST data
            try:
                post_data = {
                'prompt': "USER: Describe what you see and recognize in this image: [img-1] \nASSISTANT: ",
                'n_predict': 256,
                'image_data': [{"data": base64_image, "id": 1}],
                'ignore_eos': False,
                'temperature': 0.1
                }

                # Encode the data as JSON
                json_data = json.dumps(post_data)

                # Set the request headers
                headers = {
                    'Content-Type': 'application/json',
                }

                # Specify the URL
                llava_url = "http://localhost:8007/completion"

                # Perform the HTTP POST request for image analysis
                async with ClientSession() as session:
                    async with session.post(llava_url, headers=headers, data=json_data) as response:
                        if response.status == 200:
                            response_data = await response.json()
                            image_description = response_data['content']

                            # Combine image description and recognized text
                            combined_description = f"Image Description: {image_description}\n\Text Within The Image: {recognized_text}"

                            # Send the response back to the Discord channel
                            # await message.channel.send(combined_description, reference=message)
                            return combined_description
                        else:
                            # Handle unexpected status code
                            errorstr = f"Error: The server responded with an unexpected status code: {response.status}"
                            await util.write_to_log(errorstr)
                            combined_description = f"Text Within The Image: {recognized_text}"
                            return combined_description 
            except e:
                combined_description = f"Text Within The Image: {recognized_text}"
                return combined_description 


    except Exception as e:
        # Handle any other exception that was not explicitly caught
        error_msg = f"An error occurred: {str(e)}"
        await util.write_to_log(error_msg)

        return "Image and Text Recognition Error"
    return None