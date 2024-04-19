import os
import io
import json
import boto3
from typing import Dict, Union, Tuple, List
from PIL import Image

### CONTSTANTS ###
IMAGE_PATH = "data/jpg/december_1994"
LAYOUT_PATH = "layout/december_1994"
OCR_PATH = "ocr/aws_extract/december_1994"


def load_json_file(file_path: str) -> dict:
    """
    Load JSON data from a file.

    Parameters:
    - file_path (str): The path to the JSON file.

    Returns:
    dict: The loaded JSON data.
    """
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    return data


def get_image_and_layout(desired_image: str) -> Tuple[Image.Image, dict]:
    """
    Load an image and its layout information.

    Parameters:
    - desired_image (str): The name of the image file.

    Returns:
    tuple: A tuple containing a PIL Image and layout information.
    """
    image_path = f"{IMAGE_PATH}/{desired_image}"
    layout_path = f"{LAYOUT_PATH}/{desired_image.replace('.jpeg', '_layout.json')}"
    image = Image.open(image_path)
    layout = load_json_file(layout_path)

    return image, layout


def save_pil_image_to_file(pil_image: Image.Image, folder: str, filename: str) -> None:
    """
    Save a PIL Image to a file.

    Parameters:
    - pil_image (Image.Image): The PIL Image to be saved.
    - folder (str): The folder where the image will be saved.
    - filename (str): The name of the image file.
    """
    image_bytes = pil_image.tobytes()

    # Convert the PIL Image to bytes
    image_bytes = io.BytesIO()
    pil_image.save(image_bytes, format='JPEG')

    image_path = f"{folder}/{filename}"
    with open(image_path, 'wb') as file:
        file.write(image_bytes.getvalue())

    return image_bytes


def save_list_to_json(my_list: List[Union[int, float, str]], output_file: str) -> None:
    """
    Save a list to a JSON file.

    Parameters:
    - my_list (list): The list to be saved.
    - output_file (str): The name of the output JSON file.
    """
    with open(output_file, 'w') as json_file:
        json.dump(my_list, json_file)

    print(f"Save OCR output to {output_file}")


def perform_ocr_aws_extract(client: boto3.client,
                            img: Image.Image, 
                            layout: Dict[str, Union[str, List[Dict[str, Union[str, float, Tuple[float, float, float, float]]]]]],
                            block_number: int, 
                            blocks_folder: str) -> Dict[str, Union[str, int, str]]:
    """
    Perform Optical Character Recognition (OCR) on a cropped image.

    Parameters:
    - client (boto3.client): The AWS Textract client.
    - img (PIL.Image.Image): The input image.
    - layout (dict): Layout information for the document.
    - block_number (int): The index of the block to process.
    - blocks_folder (str): The folder where the cropped images will be saved.

    Returns:
    dict: Dictionary containing OCR results and block information.
    """
    layout_info = layout["layout"]
    block = layout_info[block_number]

    coordinates = block['coordinates']
    block_type = block['layout_type']
    reading_order = block['reading_order']

    # Crop the image section within the bounding box
    cropped_image = img.crop(coordinates)

    file_name = f"{block_type.lower()}_{reading_order}.jpeg"
    cropped_image_bytes = save_pil_image_to_file(cropped_image, blocks_folder, file_name)

    response = client.detect_document_text(Document={'Bytes': cropped_image_bytes.getvalue()})
    blk_data = []
    for blk in response["Blocks"]:
        blk_text = blk.get("Text", None)
        if blk_text is not None:
            blk_data.append(blk_text)

    blk_text = " ".join(blk_data)

    return {
       "block_type": block_type,
        "reading_order": reading_order,
       "ocr_result": blk_text
    }


if __name__ == "__main__":
    session = boto3.Session(profile_name='tobi')
    client = session.client('textract', region_name='us-east-1')

    # get list of filenames in image path
    all_imgs_names = os.listdir(IMAGE_PATH)

    # for each filename
    for img_fn in all_imgs_names:
        block_ocr_data = []
        
        # get image and layout
        image, layout = get_image_and_layout(img_fn)

        # create folder to store block ocr images
        blocks_folder = f"{OCR_PATH}/{img_fn.replace('.jpeg', '')}/block_images"
        os.makedirs(blocks_folder, exist_ok=True)

        # perform ocr on each block
        for block_number in range(len(layout["layout"])):
            ocr_data = perform_ocr_aws_extract(client, image, layout, block_number, blocks_folder)
            block_ocr_data.append(ocr_data)

        # create folder to store block ocr json
        blocks_folder_ocr = f"{OCR_PATH}/{img_fn.replace('.jpeg', '')}"
        os.makedirs(blocks_folder_ocr, exist_ok=True)
        save_list_to_json(block_ocr_data, f"{blocks_folder_ocr}/aws_extract_ocr.json")
