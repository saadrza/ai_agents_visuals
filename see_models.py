# check_models.py
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print("Checking available models...\n")

models_to_test = [
    "gpt-3.5-turbo",
    "gpt-4",
    "gpt-4-turbo",
    "gpt-4o",
    "gpt-4o-mini"
]

for model in models_to_test:
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5
        )
        print(f"✓ {model} - AVAILABLE")
    except Exception as e:
        if "does not have access" in str(e) or "model_not_found" in str(e):
            print(f"✗ {model} - NOT AVAILABLE")
        else:
            print(f"? {model} - ERROR: {e}")