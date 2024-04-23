import argparse
import os
import json
import logging
from openai import OpenAI

def setup_logging(log_file):
    """
    Set up logging configuration.

    Args:
        log_file (str): File path for logging.
    """
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        handlers=[logging.FileHandler(log_file), logging.StreamHandler()])

def call_llm(client, system_prompt, user_message, model, temperature):
    """
    Calls the OpenAI language model.

    Args:
        client: OpenAI client.
        system_prompt (str): The system prompt to be used.
        user_message (str): The user message to be sent to the model.
        model (str): The name or ID of the model to use.
        temperature (float): The sampling temperature to use.

    Returns:
        str: The response from the model.
    """
    try:
        # Call the model
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=temperature,
        )
        return completion.choices[0].message.content, True
    except Exception as e:
        logging.error(f"Failed to call OpenAI language model: {e}")
        return "failed_call", False
        

def fix_typos_in_ocr(ocr_json,
                    system_prompt,
                    model,
                    temperature,
                    api_key,
                    api_url):
    """
    Fix typos in the OCR JSON using OpenAI's text correction API.

    Args:
        ocr_json (list): List of dictionaries representing OCR results.
        system_prompt (str): The system prompt to be used.
        model (str): The name or ID of the model to use.
        temperature (float): The sampling temperature to use.
        api_key (str): OpenAI API key.
        api_url (str): OpenAI API base URL.

    Returns:
        list: List of dictionaries with corrected OCR results.
    """
    corrected_ocr_json = []

    client = OpenAI(base_url=api_url, api_key=api_key)

    for i, block in enumerate(ocr_json):
        if "ocr_result" in block:
            # Correct OCR result using OpenAI language model
            corrected_text, status = call_llm(client, system_prompt, block["ocr_result"], model, temperature)
            if i % 10 == 0:
                logging.info(f"Original text: {block['ocr_result']}")
                logging.info(f"Corrected text: {corrected_text}")
            # Update the OCR result with corrected text
            block["ocr_result"] = block["ocr_result"]
            block["ocr_result_corrected"] = corrected_text
            block["corrected"] = status

        corrected_ocr_json.append(block)

    return corrected_ocr_json

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fix typos in OCR JSON using OpenAI.')
    parser.add_argument('--model', type=str, required=True, help='Name or ID of the model to use.')
    parser.add_argument('--temperature', type=float, required=True, help='Sampling temperature to use.')
    parser.add_argument('--api_key', type=str, required=True, help='OpenAI API key.')
    parser.add_argument('--api_url', type=str, required=True, help='OpenAI API base URL.')
    parser.add_argument('--input_dir', type=str, required=True, help='Directory containing input files.')
    args = parser.parse_args()

    # Set up logging
    log_file = "fix_typos.log"
    setup_logging(log_file)

    SYSTEM_PROMPT = """You are an editor and great at fixing grammatical and typographical errors in English text. Eliminate repititions or duplicates. 
        Respond only with corrected version of any text you are given. 
        Text: Your work is truly truly remarkable, I am impressed impressed by your dedication and commitment commitment to excellence excellence 
        Your work is truly remarkable, I am impressed by your dedication and commitment to excellence. 
        Text:
    """

    logging.info(f"Model: {args.model}")
    logging.info(f"System Prompt: {SYSTEM_PROMPT}")
    logging.info(f"Temperature: {args.temperature}")
    logging.info(f"API Key: {args.api_key}")
    logging.info(f"API URL: {args.api_url}")
    logging.info(f"Input Directory: {args.input_dir}")
    logging.info(f"Log File: {log_file}")

    # Process each AWS extract OCR JSON file in the input directory
    for root, dirs, files in os.walk(args.input_dir):
        for file in files:
            if file.endswith("aws_extract_ocr.json"):
                input_file_path = os.path.join(root, file)
                output_file_path = input_file_path.replace(".json", "_fixed.json")

                # Load OCR JSON
                with open(input_file_path, "r") as f:
                    ocr_json = json.load(f)

                # Fix typos in OCR
                corrected_ocr_json = fix_typos_in_ocr(ocr_json, SYSTEM_PROMPT, args.model, args.temperature, args.api_key, args.api_url)
    

                # Log file processing
                logging.info(f"Processing file: {input_file_path}")

                # Save corrected OCR JSON
                with open(output_file_path, "w") as f:
                    json.dump(corrected_ocr_json, f, indent=4)
                    logging.info(f"Saved corrected OCR JSON to: {output_file_path}")
