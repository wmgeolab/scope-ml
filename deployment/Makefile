# Variables
SERVICE_URL := http://vllm-svc:8000
CONTENT_TYPE := application/json
MODEL_NAME := mistralai/Mistral-7B-Instruct-v0.3
PROMPT := \"Give a detailed summary of the various activities to do in San Francisco.\"
NUM_TOKENS ?= 1024

# Targets
.PHONY: list-models generate-tokens help

all: help

list-models:
	@echo "Listing available models..."
	@curl -s -X GET "$(SERVICE_URL)/v1/models" | jq

generate-tokens:
	@echo "Generating tokens..."
	@echo "curl -s -X POST \"$(SERVICE_URL)/v1/completions\" -H \"Content-Type: $(CONTENT_TYPE)\" -d '{\"model\": \"$(MODEL_NAME)\", \"prompt\": $(PROMPT), \"max_tokens\": 10, \"temperature\": 0}'"
	@curl -s -X POST "$(SERVICE_URL)/v1/completions" \
		-H "Content-Type: $(CONTENT_TYPE)" \
		-d '{"model": "$(MODEL_NAME)", "prompt": "$(PROMPT)", "max_tokens": $(NUM_TOKENS), "temperature": 0}' | jq

help:
	@echo "Available commands:"
	@echo "  make list-models     - List available models"
	@echo "  make generate-tokens - Generate tokens using default prompt"
	@echo "  make help            - Show this help message"