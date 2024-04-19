import os
from PIL import Image


def tiff_to_jpeg(input_path, output_path):
    try:
        # Open the TIFF image
        with Image.open(input_path) as img:
            # Save as JPEG
            img.convert("RGB").save(output_path, "JPEG")
        print(f"Conversion successful. Image saved to {output_path}")
    except Exception as e:
        print(f"Error: {e}")



def batch_convert_tiff_to_jpeg(source_folder, destination_folder):
    # Create the destination folder if it doesn't exist
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # Iterate through each file in the source folder
    for filename in os.listdir(source_folder):
        # Check if the file is a TIFF image
        if filename.lower().endswith(".tiff") or filename.lower().endswith(".tif"):
            # Build the paths
            input_path = os.path.join(source_folder, filename)
            
            # Remove spaces and replace with underscores in the output filename
            output_filename = filename.replace(" ", "_").replace(".tif", ".jpeg").replace(".tiff", ".jpeg")
            output_path = os.path.join(destination_folder, output_filename)

            # Call the tiff_to_jpeg function
            tiff_to_jpeg(input_path, output_path)



if __name__ == "__main__":
    source_folder = "data/tiff/December 1994"
    destination_folder = "data/jpg/december_1994"
    batch_convert_tiff_to_jpeg(source_folder, destination_folder)
