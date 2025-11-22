import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv(".env.local")

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("Error: GOOGLE_API_KEY not found in .env.local")
    exit(1)

    # Attempting to list models again to see if any others look promising, but the error was 429 on ALL.
    # The error "quota_limit_value: 0" suggests the API is not enabled or billing is off for this region.
    pass

genai.configure(api_key=api_key)

print("Listing available models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
            
    models_to_test = [
        "gemini-2.0-flash-exp",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
        "gemini-2.0-flash-thinking-exp-01-21",
        "gemini-2.0-pro-exp-02-05"
    ]

    print("\nTesting models...")
    working_model = None
    for model_name in models_to_test:
        print(f"Testing '{model_name}'...")
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Hello, are you working?")
            print(f"SUCCESS: {model_name} responded: {response.text}")
            working_model = model_name
            break
        except Exception as e:
            print(f"FAILED: {model_name} - {e}")
            
    if working_model:
        print(f"\nRECOMMENDATION: Use '{working_model}'")
    else:
        print("\nALL MODELS FAILED.")
    
except Exception as e:
    print(f"Error: {e}")
