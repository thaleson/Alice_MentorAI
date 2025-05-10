from dotenv import load_dotenv
import os

def load_env():
    load_dotenv()
    return {
        "api_key": os.getenv("API_WEB"),
        "model_url": os.getenv("URL_MODEL")
    }
