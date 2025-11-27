import os
from dotenv import find_dotenv, load_dotenv

# Look for a .env starting from this file's directory and moving upward.
dotenv_path = find_dotenv(usecwd=True)
if dotenv_path:
    # override=True in case an existing env var (like "no") masks the .env value
    load_dotenv(dotenv_path=dotenv_path, override=True)
else:
    print("No .env found via find_dotenv(); relying on existing environment variables.")

api_key = os.getenv("GOOGLE_API_KEY")
print(f"GOOGLE_API_KEY loaded: {api_key}")
