# Variables
SERVICE_URL := http://vllm-svc:8000
AUTOSCALER_URL := http://autoscaler-service:8000
CONTENT_TYPE := application/json
MODEL_NAME := mistralai/Mistral-7B-Instruct-v0.3
PROMPT := \"Give a detailed summary of the various activities to do in San Francisco.\"
NUM_TOKENS ?= 1024
SERVICE_NAME ?= internvl

## ML API
PROJECT_IDS ?=
ML_API_URL := http://ml-api-svc:8000

# Targets
.PHONY: list-models generate-tokens list-services scale-up scale-down ingest-projects help

all: help

list-models:
	@echo "Listing available models..."
	@curl -s -X GET "$(SERVICE_URL)/v1/models" | jq

list-services:
	@echo "Available services that can be scaled (use with scale-up/scale-down):"
	@echo "  - internvl"
	@echo "  - qwen2.5vl"
	@echo "  - vllm-qwen2-5"

# Scale up a service - either specified or default
scale-up:
	@SERVICE=$(filter-out $@,$(MAKECMDGOALS)); \
	if [ -z "$$SERVICE" ]; then \
		echo "Scaling up default service ($(SERVICE_NAME))..."; \
		curl -s -X POST "$(AUTOSCALER_URL)/scale/$(SERVICE_NAME)/1" | jq; \
	else \
		echo "Scaling up $$SERVICE..."; \
		curl -s -X POST "$(AUTOSCALER_URL)/scale/$$SERVICE/1" | jq; \
	fi

# Scale down a service - either specified or default
scale-down:
	@SERVICE=$(filter-out $@,$(MAKECMDGOALS)); \
	if [ -z "$$SERVICE" ]; then \
		echo "Scaling down default service ($(SERVICE_NAME))..."; \
		curl -s -X POST "$(AUTOSCALER_URL)/scale/$(SERVICE_NAME)/0" | jq; \
	else \
		echo "Scaling down $$SERVICE..."; \
		curl -s -X POST "$(AUTOSCALER_URL)/scale/$$SERVICE/0" | jq; \
	fi

generate-tokens:
	@echo "Generating tokens..."
	@curl -s -X POST "$(SERVICE_URL)/v1/completions" \
		-H "Content-Type: $(CONTENT_TYPE)" \
		-d '{"model": "$(MODEL_NAME)", "prompt": "$(PROMPT)", "max_tokens": $(NUM_TOKENS), "temperature": 0}' | jq

ingest-projects:
	@if [ -z "$(PROJECT_IDS)" ]; then \
		echo "Error: PROJECT_IDS is required. Use: make ingest-projects PROJECT_IDS=9467,9468"; \
		exit 1; \
	fi
	@echo "Starting ingestion for projects: $(PROJECT_IDS)"
	@PROJECT_IDS_JSON=$$(echo "[\"$$(echo $(PROJECT_IDS) | sed 's/,/\",\"/g')\"]"); \
	curl -N -X POST "$(ML_API_URL)/ingestion/projects" \
		-H "Content-Type: $(CONTENT_TYPE)" \
		-d "{\"project_ids\": $$PROJECT_IDS_JSON}"

help:
	@echo "Available commands:"
	@echo "  make list-models                 - List available models"
	@echo "  make list-services               - List available autoscaler services"
	@echo "  make scale-up [service_name]     - Scale up service (use default if no name provided)"
	@echo "  make scale-down [service_name]   - Scale down service (use default if no name provided)"
	@echo "  make generate-tokens             - Generate tokens using default prompt"
	@echo "  make ingest-projects PROJECT_IDS=X,Y - Ingest specified GEF project IDs"
	@echo "  make help                        - Show this help message"

# Special target to handle service names as arguments
%:
	@: