SRC_DIR := data/old_sources/newspapers/scans/silver/aws_text_extract/ocr/december_1994
MODEL := "lmstudio-community/Meta-Llama-3-8B-Instruct-GGUF"
TEMPERATURE := 0
API_KEY := "lm-studio"
API_URL := "http://localhost:1234/v1"


fix_typos:
	python src/data_processing/old_sources/newspapers/scans/aws_text_extract/step_4_fix_typos.py \
		--model $(MODEL) \
		--temperature $(TEMPERATURE) \
		--api_key $(API_KEY) \
		--api_url $(API_URL) \
		--input_dir $(SRC_DIR)
