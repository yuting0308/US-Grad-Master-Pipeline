import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("[ERROR] GEMINI_API_KEY not found in .env")
    exit()

client = genai.Client(api_key=api_key)

print("=== Available Gemini Models for Your API Key ===")
try:
    for model in client.models.list():
        # 印出模型名稱與支援的功能
        print(f"Model ID: {model.name}")
except Exception as e:
    print(f"[ERROR] Failed to list models: {e}")