import os
import sys

from dotenv import load_dotenv

if not load_dotenv(".env") and not load_dotenv("../.env"):
    print("! load_dotenv failed. Continuing...", file=sys.stderr)


GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", None)
GOOGLE_SEARCH_ENGINE_ID = os.environ.get("GOOGLE_SEARCH_ENGINE_ID", None)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", None)
MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-4o")
SMALL_MODEL_NAME = os.environ.get("SMALL_MODEL_NAME", "gpt-4o-mini")

SEARCH_CACHE = "cache_search"
DOWNLOAD_CACHE = "cache_downloads"

SAFETY_TOKEN_LIMIT = 20000
LLM_MODEL_PRICES = {
    "gpt-4o": {"input": 5, "output": 15},
    "gpt-4o-mini": {"input": 0.15, "output": 0.6},
}

if not GOOGLE_API_KEY:
    print("! GOOGLE_API_KEY not set.", file=sys.stderr)
if not GOOGLE_SEARCH_ENGINE_ID:
    print("! GOOGLE_SEARCH_ENGINE_ID not set.", file=sys.stderr)
if not OPENAI_API_KEY:
    print("! OPENAI_API_KEY not set.", file=sys.stderr)
if not MODEL_NAME:
    print("! MODEL_NAME not set.", file=sys.stderr)
if not SMALL_MODEL_NAME:
    print("! SMALL_MODEL_NAME not set.", file=sys.stderr)
