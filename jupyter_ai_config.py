# jupyter_ai_config.py

import os
from jupyter_ai_magics import config

# Read API key from environment variable
api_key = os.getenv('OPENAI_API_KEY')

if not api_key:
    raise ValueError("No API key found for OpenAI. Please set the OPENAI_API_KEY environment variable.")

config.api_keys = {
    "openai": api_key
}

# Define default language model and embedding model after activation
def set_defaults():
    config.default_llm = "openai:gpt-3.5-turbo"
    config.default_embedding_model = "openai:embed-gpt-3.5-turbo"

# Call set_defaults() to set defaults after extension activation
set_defaults()
