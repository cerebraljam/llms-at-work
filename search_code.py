import os

import requests
from bs4 import BeautifulSoup
import hashlib
import json
import re
import time
import unicodedata
import random
from datetime import datetime, timedelta

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from constants import GOOGLE_API_KEY, GOOGLE_SEARCH_ENGINE_ID

if not GOOGLE_SEARCH_ENGINE_ID:
    raise ValueError("Please set the GOOGLE_SEARCH_ENGINE_ID environment variable")


def google_search(query, num_results=3, max_retries=2, delay=1):
    """
    Perform a Google search and return the top results with throttling and retry mechanism.

    :param query: The search query string
    :param num_results: Number of top results to return (default is 3)
    :param max_retries: Maximum number of retries in case of rate limiting (default is 3)
    :param delay: Delay in seconds between retries (default is 1)
    :return: List of dictionaries containing 'title' and 'link' for each result
    """

    service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
    num_results = min(max(1, num_results), 10)

    for attempt in range(max_retries):
        try:
            res = (
                service.cse()
                .list(q=query, cx=GOOGLE_SEARCH_ENGINE_ID, num=num_results)
                .execute()
            )

            results = []
            for item in res.get("items", []):
                results.append({"title": item["title"], "link": item["link"]})

            return results

        except HttpError as e:
            if e.resp.status in [429, 500, 503]:  # Rate limit error codes
                if attempt < max_retries - 1:  # If it's not the last attempt
                    wait_time = delay * (2**attempt)  # Exponential backoff
                    print(f"Rate limit hit. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print("Max retries reached. Unable to complete the request.")
                    return []
            else:
                print(f"An HTTP error occurred: {e}")
                return []

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return []

    return []  # If we've exhausted all retries


def sanitize_text(text):
    """
    Sanitize the input text by normalizing Unicode characters, replacing problematic characters,
    removing unnecessary whitespace, and ensuring compatibility with both English and Japanese text.
    """

    # Normalize Unicode characters to NFC form to ensure consistency
    text = unicodedata.normalize("NFC", text)

    # Replace problematic Unicode punctuation with their ASCII equivalents
    replacements = {
        "\u2018": "'",  # Left single quotation mark
        "\u2019": "'",  # Right single quotation mark
        "\u201C": '"',  # Left double quotation mark
        "\u201D": '"',  # Right double quotation mark
        "\u2013": "-",  # En dash
        "\u2014": "-",  # Em dash
        "\u00A0": " ",  # Non-breaking space
        "\u3000": " ",  # Ideographic space (full-width space used in Japanese)
    }
    for orig, repl in replacements.items():
        text = text.replace(orig, repl)

    # Remove zero-width spaces and other non-printable characters (except whitespace characters)
    text = "".join(c for c in text if c.isprintable() or c in "\n\r\t")

    # Replace sequences of multiple spaces with a single space (but keep newlines intact)
    text = re.sub(r"[ ]{2,}", " ", text)

    # Replace sequences of more than two newlines with exactly two newlines to avoid excessive spacing
    text = re.sub(r"(\n\s*){3,}", "\n\n", text)

    # Trim leading and trailing whitespace from each line
    text = "\n".join(line.strip() for line in text.splitlines())

    # Remove any remaining instances of multiple spaces created by the previous step
    text = re.sub(r" {2,}", " ", text)

    # Ensure the text doesn't start or end with unnecessary whitespace
    return text.strip()


def download_content(url, cache_dir="download_cache", cache_duration=30):
    """
    Scrape text content from a given URL, removing HTML tags.
    Uses caching to store and retrieve content.

    :param url: The URL to scrape
    :param cache_dir: Directory to store cache files (default: 'download_cache')
    :param cache_duration: Cache duration in days (default: 30)
    :return: Cleaned text content from the URL
    """

    # Create cache directory if it doesn't exist
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    # Generate a filename for the cache based on the URL
    cache_filename = hashlib.md5(url.encode()).hexdigest() + ".json"
    cache_path = os.path.join(cache_dir, cache_filename)

    if os.path.exists(cache_path) and os.path.getsize(cache_path) > 0:
        if datetime.now() - datetime.fromtimestamp(
            os.path.getmtime(cache_path)
        ) < timedelta(days=cache_duration):
            with open(cache_path, "r", encoding="utf-8") as cache_file:
                cache_data = json.load(cache_file)
                if "text/html" in cache_data.get("content_type", ""):
                    return cache_data["content"]

    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:131.0) Gecko/20100101 Firefox/131.0",
    ]

    headers = {"User-Agent": random.choice(user_agents)}

    try:
        time.sleep(random.uniform(1, 3))  # Random delay between 1 and 3 seconds
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = "utf-8"
        response.raise_for_status()  # Raise an exception for bad status codes
    except requests.exceptions.Timeout:
        return None
    except requests.exceptions.ConnectionError:
        return None
    except requests.exceptions.RequestException as e:
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            print(f"Rate limited, retrying after {retry_after} seconds")
            time.sleep(retry_after)
            return download_content(url, cache_dir="download_cache", cache_duration=30)
    except Exception as e:
        return None

    content_type = response.headers.get("Content-Type", "").lower()
    if "text/html" not in content_type:
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()

    # Get text
    text = soup.get_text()

    # Break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())

    # Break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))

    # Drop blank lines
    text = "\n".join(chunk for chunk in chunks if chunk)

    # Cache the scraped content
    cache_data = {
        "url": url,
        "timestamp": time.time(),
        "content": text,
        "content_type": content_type,
    }
    with open(cache_path, "w", encoding="utf-8") as cache_file:
        json.dump(cache_data, cache_file, ensure_ascii=False, indent=2)

    return text
