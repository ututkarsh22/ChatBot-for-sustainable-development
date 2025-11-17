from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()
api_key = os.getenv("GEMINI_API")

if not api_key:
    raise ValueError("Missing GEMINI_API in environment variables")

genai.configure(api_key=api_key)

# List available models
models = genai.list_models()

for model in models:
    print(f"Model Name: {model.name}")
    print(f"Supported generation methods: {model.supported_generation_methods}")
    print("-" * 50)
