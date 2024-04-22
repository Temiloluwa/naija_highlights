import os
import cv2
import argparse
import logging
from typing import Tuple

# Set up logging to file and console
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler('preprocessing.log'),
                                logging.StreamHandler()])

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def preprocess_image_for_ocr(image_path: str,
                              output_folder: str,
                              clip_limit: float = 2.0,
                              tile_grid_size: Tuple[int, int] = (4, 4)) -> None:
    """
    Preprocesses an image for OCR (Optical Character Recognition) by applying CLAHE and Otsu's thresholding.

    Args:
        image_path (str): Path to the input image.
        output_folder (str): Folder to save the preprocessed images.
        clip_limit (float): Threshold for contrast limiting in CLAHE. Default is 2.0.
        tile_grid_size (Tuple[int, int]): Size of grid for histogram equalization in CLAHE. Default is (4, 4).
    """
    # Read the image in grayscale
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Create a CLAHE object
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)

    # Apply CLAHE to the image
    result = clahe.apply(img)

    # Apply Otsu's thresholding
    _, result = cv2.threshold(result, 0, 255, cv2.THRESH_OTSU)

    # Extract filename from the path
    filename = os.path.basename(image_path)
    # Generate output path
    output_path = os.path.join(output_folder, f"preprocessed_{filename}")

    # Save the thresholded image
    cv2.imwrite(output_path, result, [int(cv2.IMWRITE_JPEG_QUALITY), 100])

    logger.info(f"Processed image {filename} saved to {output_folder}")


if __name__ == "__main__":
    # Parsing command line arguments
    parser = argparse.ArgumentParser(description='Preprocess images in a folder for OCR.')
    parser.add_argument('input_folder', type=str, help='Folder containing input images')
    parser.add_argument('output_folder', type=str, help='Folder to save preprocessed images')
    parser.add_argument('--clip_limit', type=float, default=2.0, help='Threshold for contrast limiting in CLAHE')
    parser.add_argument('--tile_grid_size', nargs=2, type=int, default=[4, 4], metavar=('rows', 'columns'),
                        help='Size of grid for histogram equalization in CLAHE')
    args = parser.parse_args()

    # Converting tile_grid_size argument to a tuple
    tile_grid_size = tuple(args.tile_grid_size)

    # Ensure output folder exists, if not create it
    os.makedirs(args.output_folder, exist_ok=True)


    # Process each image in the input folder
    for filename in os.listdir(args.input_folder):
        if filename.endswith(('.jpg', '.jpeg', '.png', '.tif', '.tiff')):
            input_image_path = os.path.join(args.input_folder, filename)
            preprocess_image_for_ocr(input_image_path, args.output_folder, args.clip_limit, tile_grid_size)
