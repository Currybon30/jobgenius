import os
from dotenv import load_dotenv
load_dotenv()

AI_MODEL_NAME = "qwen2.5:7b"
OLLAMA_HOST = "http://localhost:11434"
JSEARCH_HOST = "https://jsearch.p.rapidapi.com"
JSEARCH_HEADERS = {
    'Content-Type': 'application/json',
    'x-rapidapi-host': 'jsearch.p.rapidapi.com',
    'x-rapidapi-key': os.getenv("RAPIDAPI_KEY")
}