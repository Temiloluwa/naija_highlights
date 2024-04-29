# OCR on OLD Nigerian Newspapers

## Overview

OCR is performed with Text extract in the following steps:

1. convert tiff to jpg
2. extract the layout or bounded boxes in the image 
3. crop the image using the bounding box information and execute OCR

## Done Tasks

1. The `src/get_document_layout.py` uses Amazon Textextract to get the document layout and stores the information as json files.

2. The module `src/perform_ocr_aws_text_extract.py` performs OCR using AWS Textextract.
    - Stores OCR information at `ocr/aws_extract/december_1994`
    - Each image's OCR information is captured in a folder named just like it.
    - The bounding boxes discovered when extracting the layout are cropped out of the image
    - Then OCR is performed on the cropped images

## To-Do Tasks

1. Cluster related OCR blocks or bounding boxes: those that correspond to the same article.
    - For each image, there are multiple articles present
    - Each article is composed of multiple blocks or bounding boxes
    - Utilize an LLM to match blocks that belong to the same article. Afterwards, the articles are created by combining the OCR texts of the constituent blocks.

2. Improve the OCR performance by
    - Improving the Image quality
    - Exploring other OCR libraries
    - Please modify `perform_ocr` function in module `src/aws-text-extract/exp_perform_ocr.ipynb` to improve the OCR performance. 