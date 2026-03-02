import os

api_key = None
try:
    with open(".env", "r") as f:
        for line in f:
            if line.startswith("GEMINI_API_KEY"):
                api_key = line.strip().split("=")[1]
except FileNotFoundError:
    print(".env file wasn't found, please create it.")
    exit()

if not api_key:
    print("API key not found in .env file.")
    exit()

genai.configure(api_key=api_key)

print("🚀 Fetching all available Gemini Models for your API key...\n")
print("-" * 50)

# Lists all models from Google's server
for model in genai.list_models():
    # Models that can generate text/content
    if "generateContent" in model.supported_generation_methods:
        print(f"Model Name: {model.name}")
        print(f"Description: {model.description}")
        print("-" * 50)