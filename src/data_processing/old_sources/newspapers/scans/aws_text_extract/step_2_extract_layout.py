import io
import os
import json 
import asyncio
import boto3
from PIL import Image, ImageDraw, ImageColor
from typing import Tuple, Dict, List, Union
from dotenv import load_dotenv

load_dotenv()

async def get_coordinates(box: Dict[str, float], width: int, height: int, extra_width: float = 0.005) -> Tuple[float, float, float, float]:
    """
    Calculate coordinates (X1, Y1, X2, Y2) of a bounding box within an image.

    Parameters:
    - box (dict): A dictionary containing 'Left', 'Top', 'Width', and 'Height' values representing the bounding box.
    - width (int): Width of the image.
    - height (int): Height of the image.
    - extra_width (float): Additional width to be considered for the bounding box.

    Returns:
    tuple: A tuple containing X1, Y1, X2, Y2 coordinates of the bounding box.
    """
    X1 = width * (box['Left'] - extra_width)
    Y1 = height * box['Top']
    X2 = X1 + (width * (box['Width'] + 2 * extra_width))
    Y2 = Y1 + (height * box['Height'])

    return X1, Y1, X2, Y2


async def process_image_async(client, s3_resource, bucket: str, document: str, show_image: bool = True)\
             -> Dict[str, Union[str, List[Dict[str, Union[str, float, Tuple[float, float, float, float]]]]]]:
    """
    Analyze the layout of a document, draw bounding boxes, and perform OCR on text blocks.

    Parameters:
    - s3_resource: The resource to the S3 service.
    - client: The AWS Textract client.
    - bucket (str): The S3 bucket containing the document.
    - document (str): The name of the document.
    - show_image (bool): Whether to display the image with bounding boxes.

    Returns:
    dict: A dictionary containing information about the processed document layout.
    """
    layout_color_palette: Dict[str, Union[Tuple[int, int, int], str]] = {
        "LAYOUT_TITLE": ImageColor.getrgb("#e41a1c"),
        "LAYOUT_HEADER": ImageColor.getrgb("#377eb8"),
        "LAYOUT_FOOTER": ImageColor.getrgb("#4daf4a"),
        "LAYOUT_SECTION_HEADER": ImageColor.getrgb("#984ea3"),
        "LAYOUT_PAGE_NUMBER": ImageColor.getrgb("#ff7f00"),
        "LAYOUT_LIST": ImageColor.getrgb("#ffff33"),
        "LAYOUT_FIGURE": ImageColor.getrgb("#a65628"),
        "LAYOUT_TABLE": ImageColor.getrgb("#f781bf"),
        "LAYOUT_KEY_VALUE": ImageColor.getrgb("#999999"),
        "LAYOUT_TEXT": "yellow"
    }
    try:
        # Get the document from S3
        s3_object = s3_resource.Object(bucket, document)
        s3_response = s3_object.get()

        stream = io.BytesIO(s3_response['Body'].read())
        image = Image.open(stream)

        # Analyze the document
        image_binary = stream.getvalue()
        response = client.analyze_document(Document={'Bytes': image_binary}, FeatureTypes=["LAYOUT"])

        # Get the text blocks
        blocks = response['Blocks']
        width, height = image.size
        
        print(f'Detecting Document Layout for {document}')
        layout_information: List[Dict[str, Union[str, float, Tuple[float, float, float, float]]]] = []

        # Create image showing bounding box/polygon the detected lines/text
        for block in blocks:
            draw = ImageDraw.Draw(image)
            block_type = block['BlockType']
            block_color = layout_color_palette.get(block_type, None)
            if block_color:
                info = {}
                img_coords = await get_coordinates(block['Geometry']['BoundingBox'], width, height)

                if show_image:
                    draw.rectangle(img_coords, outline=block_color, width=3)
                info = {
                    "id": block['Id'],
                    "layout_type": block_type,
                    "coordinates": img_coords,
                    "block_color": block_color,
                    "reading_order": len(layout_information) + 1
                }
                layout_information.append(info)

        # Display the image
        if show_image:
            image.show()

        layout_information = {"bucket": bucket, "document": document, "layout": layout_information}

        # Save the image with bounding boxes
        result_image_path = document.replace(".jpeg", "_layout.json").replace("/jpeg", "/layout")
        local_image_fn = result_image_path.split("/")[-1]
        layout_json_path = result_local_folder + "/" + local_image_fn 
        with open(layout_json_path, 'w') as json_file:
            json.dump(layout_information, json_file)

        # Upload the result image to the same subfolder
        s3_resource.Object(bucket, result_image_path).upload_file(layout_json_path)

        return layout_information
    
    except Exception as e:
        print(f"Error processing {document}: {str(e)}")
        return {"bucket": bucket, "document": document, "error": str(e)}


async def process_all_images_async(s3_client, s3_resource, bucket, prefix):
    document_list = [obj.key for obj in s3_resource.Bucket(bucket).objects.filter(Prefix=prefix) if obj.key.endswith('.jpeg')]
    tasks = [process_image_async(s3_client, s3_resource, bucket, document, False) for document in document_list]
    return await asyncio.gather(*tasks)

async def main():
    result = await process_all_images_async(s3_client, s3_resource, bucket_name, subfolder_prefix)
    return result

if __name__ == "__main__":
    # AWS S3 configuration
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")

    # BUCKET configuration
    bucket_name = 'hifeyinc-cluster'
    subfolder_prefix = 'projects/newspaper-ocr/data/jpeg/december_1994/'
    result_local_folder = "./layout/december_1994"
    os.makedirs(result_local_folder, exist_ok=True)

    # Create an S3 client and resource
    s3_client = boto3.client('textract', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    s3_resource = boto3.resource('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)

    asyncio.run(main())
