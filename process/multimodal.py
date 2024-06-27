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
    recognized_text = ""
    recognized_image = ""
    image_description = ""
    try:
        # Process each attachment (actually just one for now)
        for attachment in message.attachments:
            # Check if it is an image based on content type
            image_bytes = await attachment.read()
            if any(attachment.filename.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']):
                print(attachment.filename.lower())
                if attachment.filename.lower().endswith('.webp'):
                    image_bytes = await util.convert_webp_bytes_to_png(image_bytes)
                #image_description = await process_image(image_bytes)
                recognized_text = await process_text(image_bytes)
                recognized_image = await process_image(attachment)
                image_description = f"Image Description: {recognized_image} | Text Within Image: {recognized_text}"
                return image_description
            else:
                # Check if it is a link to an images
                if attachment.url:
                    if attachment.filename.lower().endswith('.webp'):
                        image_bytes = await util.convert_webp_bytes_to_png(image_bytes)
                    if any(attachment.url.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']):
                        # You would typically fetch the image from the URL here
                        # For example, using aiohttp to fetch the image
                        async with ClientSession() as session:
                            async with session.get(attachment.url) as response:
                                if response.status == 200:
                                    if attachment.filename.lower().endswith('.webp'):
                                        image_bytes = await util.convert_webp_bytes_to_png(image_bytes)
                                    recognized_text = await process_text(image_bytes)
                                    recognized_image = await process_image(attachment)
                                    return image_description
    except Exception as e:
        print(f"An error occurred: {e}")

async def process_text(image_bytes):
    try:        
        image = Image.open(BytesIO(image_bytes))
        # OCR~
        recognized_text = pytesseract.image_to_string(image).strip()
        #Toggle Only Text Recognition
        return recognized_text 
    except Exception as e:
        # Handle any other exception that was not explicitly caught
        error_msg = f"An error occurred: {str(e)}"
        await util.write_to_log(error_msg)

        return "Image Text Recognition Error"
    
async def process_image(image_bytes):
    try:
        model = config.florence
        processor = config.florence_processor

        prompt = "<OD>"

        #url = "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/transformers/tasks/car.jpg?download=true"
        image = Image.open(BytesIO(image_bytes))

        inputs = processor(text=prompt, images=image, return_tensors="pt")

        generated_ids = model.generate(
            input_ids=inputs["input_ids"],
            pixel_values=inputs["pixel_values"],
            max_new_tokens=1024,
            do_sample=False,
            num_beams=3
        )
        generated_text = processor.batch_decode(generated_ids, skip_special_tokens=False)[0]

        parsed_answer = processor.post_process_generation(generated_text, task="<OD>", image_size=(image.width, image.height))

        
        return parsed_answer
    except Exception as e:
        print(e)
        return ""