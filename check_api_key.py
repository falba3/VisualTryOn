import os
from dotenv import load_dotenv
load_dotenv()


api_key = os.getenv("GOOGLE_API_KEY")
print(f"GOOGLE_API_KEY loaded: {api_key}")