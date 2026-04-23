#!/bin/bash
# Generate MT data from spec
#
# Parameters:
# - specified_domains: skips domain generation, uses specified domains instead
# - n_doc_types: number of document types to generate *per subdomain*
# - n_doc_ideas: number of document ideas to generate *per document type*
# - total docs = n_domains * n_subdomains * n_doc_types * n_doc_ideas
# - facts_path: optional path to facts document to use as assertion context
#
# Set USE_BATCH_API to control document generation mode:
# - false: Regular InferenceAPI for all steps (faster for small datasets)
# - true:  BatchInferenceAPI for document generation (better for large datasets >5k docs)
#          Batch jobs typically take 5-10 minutes but can take hours

# Config
SPEC_TYPE="default" # set to "rules" if spec only contains numbered rules/policies; otherwise, leave as "default"

DATASET_NAME="rules_spec"
PRINCIPLE_NAME="harmlessness"
SPEC_FILE_NAME="rules" # "data/spec/example/rules.txt" -> "rules"
MODEL_NAME="Qwen"
PROVIDER_NAME="Alibaba"
MODEL_ID="claude-opus-4-6"

N_DOC_TYPES=10
N_DOC_IDEAS=20
MAX_OUTPUT_TOKENS=64000
TEMPERATURE=1.0
ANTHROPIC_TAG="ANTHROPIC_HIGH_PRIORITY_API_KEY"  # For domains/subdomains/assertions generation (always needed)
ANTHROPIC_BATCH_TAG="ANTHROPIC_BATCH_API_KEY"    # For documents generation (only if USE_BATCH_API=true)
OPENAI_TAG="OPENAI_API_KEY"
ENABLE_CACHE=false
MAX_CONCURRENT=30
USE_BATCH_API=true

# Run generation
CMD="python src/msm/generate_data_from_spec.py \
    --dataset_name \"$DATASET_NAME\" \
    --principle_name \"$PRINCIPLE_NAME\" \
    --spec_file_name \"$SPEC_FILE_NAME\" \
    --model_name \"$MODEL_NAME\" \
    --provider_name \"$PROVIDER_NAME\" \
    --model_id \"$MODEL_ID\" \
    --n_doc_types $N_DOC_TYPES \
    --n_doc_ideas $N_DOC_IDEAS \
    --max_output_tokens $MAX_OUTPUT_TOKENS \
    --temperature $TEMPERATURE \
    --spec_type \"$SPEC_TYPE\" \
    --anthropic_tag \"$ANTHROPIC_TAG\" \
    --anthropic_batch_tag \"$ANTHROPIC_BATCH_TAG\" \
    --openai_tag \"$OPENAI_TAG\" \
    --enable_cache $ENABLE_CACHE \
    --max_concurrent_requests $MAX_CONCURRENT \
    --use_batch_api $USE_BATCH_API"

eval $CMD
