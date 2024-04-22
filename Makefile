SRC_DIR := data/old_sources/newspapers/scans/silver/aws_text_extract/ocr/december_1994
MODEL := "FaradayDotDev/llama-3-8b-Instruct-GGUF"
SYSTEM_PROMPT := "You are an editor and great at fixing grammatical and typographical errors in English text. Respond only with corrected version of any text you are given."
TEMPERATURE := 0
API_KEY := "lm-studio"
API_URL := "http://localhost:1234/v1"


fix_typos:
	python src/data_processing/old_sources/newspapers/scans/aws_text_extract/step_4_fix_typos.py \
		--model $(MODEL) \
		--system-prompt $(SYSTEM_PROMPT) \
		--temperature $(TEMPERATURE) \
		--api-key $(API_KEY) \
		--api-url $(API_URL) \
		--input-dir $(SRC_DIR)
