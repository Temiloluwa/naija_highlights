import cv2

def preprocess_image_for_ocr(image_path,
                              output_path_preprocessed,
                              clip_limit=2.0,
                              tile_grid_size=(4, 4)):
    # Read the image in grayscale
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Create a CLAHE object
    clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)

    # Apply CLAHE to the image
    result = clahe.apply(img)

    # Apply Otsu's thresholding
    _, result = cv2.threshold(result, 0, 255, cv2.THRESH_OTSU)

    # Save the thresholded image
    cv2.imwrite(output_path_preprocessed, result, [int(cv2.IMWRITE_JPEG_QUALITY), 100])

    print(f"processed image {image_path}")


# Example usage
preprocess_image_for_ocr('/content/PM News December 1_1994_Pg 3.tif',
                         'original_image.jpg', 'preprocessed_image.jpg')