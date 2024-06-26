# This is the Multi Modal Part
# For now this will only support Image Recognition, but later on who knows???
from io import BytesIO
import io
import json
from PIL import Image
import pytesseract

import discord
from aiohttp import ClientSession
import config
import util
from aiohttp import ClientSession
from aiohttp import ClientTimeout
from aiohttp import TCPConnector

from aiohttp import ClientSession
from aiohttp import ClientTimeout
from aiohttp import TCPConnector
async def read_image(message):
    try:
        # Process each attachment (actually just one for now)
        for attachment in message.attachments:
            # Check if it is an image based on content type
            if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']):
                image_bytes = await attachment.read()
                print(attachment.filename.lower())
                if attachment.filename.lower().endswith('.webp'):
                    image_bytes = await util.convert_webp_bytes_to_png(image_bytes)
                #image_description = await process_text(image_bytes)
                image_description = await process_image(image_bytes)
                print("Process Image Result: "+image_description)
                return image_description
            else:
                # Check if it is a link to an image
                if attachment.url:
                    if attachment.filename.lower().endswith('.webp'):
                        image_bytes = await util.convert_webp_bytes_to_png(image_bytes)
                    if any(attachment.url.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']):
                        # You would typically fetch the image from the URL here
                        # For example, using aiohttp to fetch the image
                        async with ClientSession() as session:
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
            image_recognition_result = "Image Recognition Failed"
            # Process each attachment (actually just one for now)
            # Check if it is an image based on content type
            
            #Toggle Only Text Recognition
            return recognized_text

            if not recognized_text:
                recognized_text = "No text recognized in the image."

            # Define the POST data
            try:
                post_data = await create_image_prompt(base64_image)

                # Specify the URL
                timeout = ClientTimeout(total=600)
                connector = TCPConnector(limit_per_host=10)
                async with ClientSession(timeout=timeout, connector=connector) as session:
                    try:
                        async with session.post(config.text_api["address"] + config.text_api["generation"], headers=config.text_api["headers"], data=post_data) as response:
                            if response.status == 200:
                                try:
                                    json_response = await response.json()
                                    print(json_response)
                                    image_recognition_result = json_response['results'][0]['text']
                                    image_recognition_result = remove_string_before_final(image_recognition_result)
                                    combined_description = f"Image Recognition Result: {image_recognition_result} | Text Within The Image: {recognized_text}"
                                    return combined_description
                                except json.decoder.JSONDecodeError as e:
                                    # Handle the case where response is not JSON-formatted
                                    print(f"Failed to decode JSON response: {e}")
                                    text_response = await response.text()
                                    print(f"Response text was: {text_response}")
                            else:
                                # Handle non-200 responses here
                                print(f"HTTP request failed with status: {response.status}")
                    except Exception as e:
                        # Handle any other exceptions
                        print(e)
            except Exception as e:
                print(e)
                combined_description = f"Image Recognition Result: Fail | Text Within The Image: {recognized_text}"
                return combined_description 


    except Exception as e:
        # Handle any other exception that was not explicitly caught
        error_msg = f"An error occurred: {str(e)}"
        await util.write_to_log(error_msg)

        return "Image Text Recognition Error"
    return "Image and Text Recognition Error"


async def create_image_prompt(
    image
) -> str:
    
    prompt = "\n### Instruction:Briefly describe the following image\n### Response:\n"

    stopping_strings = ["### Instruction:","### Response:","["]
    
    data = config.text_api["parameters"]
    data.update({"prompt": prompt})
    data.update({"stop_sequence": stopping_strings})
    data.update({"images":[image]})
    data_string = json.dumps(data)
    data.update({"images":""})
    return data_string

def remove_string_before_final(data: str) -> str:
    # Check if the data ends with the trim string
    trim = "### Instruction:"
    if data.endswith(trim):
        # If it does, remove the trim string from the end
        return data[:-len(trim)]
    # If not, return the original data
    return data
