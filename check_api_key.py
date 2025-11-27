#!/usr/bin/env python3
"""
Quick check to confirm GOOGLE_API_KEY is available (from env or .env).

Usage:
    python check_api_key.py
"""

import os
from pathlib import Path

from dotenv import find_dotenv, load_dotenv
load_dotenv()

def main() -> None:
    # env_path = find_dotenv(".env", usecwd=True)
   # if env_path:
    #    load_dotenv(env_path)
    #else:
     #   print(".env not found via find_dotenv; relying on environment variables.")

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise SystemExit("GOOGLE_API_KEY not found. Add it to .env (or export it) and rerun from repo root.")

    print(f"GOOGLE_API_KEY loaded: {api_key}")


if __name__ == "__main__":
    main()
