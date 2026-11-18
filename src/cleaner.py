import os
import re
import time
import hashlib
import logging
from typing import Optional
from curl_cffi import requests as curl_requests
from bs4 import BeautifulSoup

# Configure structured logging to both console and pipeline.log
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("pipeline.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class WebContentCleaner:
    def __init__(self, cache_dir: str = "raw_cache", max_chars: int = 12000):
        self.cache_dir = cache_dir
        self.max_chars = max_chars
        os.makedirs(self.cache_dir, exist_ok=True)

    def _get_cache_path(self, url: str) -> str:
        """Generate a deterministic cache filename using URL SHA-256 hash."""
        url_hash = hashlib.sha256(url.encode("utf-8")).hexdigest()[:16]
        return os.path.join(self.cache_dir, f"{url_hash}.txt")

    def clean_html(self, html_content: str) -> str:
        """Strip boilerplate HTML tags and normalize whitespace to reduce token count."""
        soup = BeautifulSoup(html_content, "html.parser")

        # Remove non-content structural elements
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript", "iframe"]):
            tag.decompose()

        raw_text = soup.get_text(separator="\n", strip=True)
        # Collapse consecutive blank lines and excessive spaces
        lines = [re.sub(r"\s+", " ", line).strip() for line in raw_text.splitlines()]
        cleaned_text = "\n".join(line for line in lines if line)

        return cleaned_text[: self.max_chars]

    def fetch_and_clean(
        self, url: str, use_cache: bool = True, retries: int = 2, delay: float = 1.5
    ) -> str:
        """Fetch webpage via TLS impersonation, clean DOM, and persist snapshot to raw_cache/."""
        if not url or not url.startswith("http"):
            return ""

        cache_path = self._get_cache_path(url)

        # Return cached snapshot if available
        if use_cache and os.path.exists(cache_path):
            logger.info(f"[CACHE HIT] Loaded snapshot for: {url}")
            with open(cache_path, "r", encoding="utf-8") as f:
                return f.read()

        for attempt in range(1, retries + 1):
            try:
                time.sleep(delay)  # Polite rate limiting
                logger.info(f"[FETCH] Requesting ({attempt}/{retries}): {url}")
                response = curl_requests.get(url, impersonate="chrome120", timeout=20)

                if response.status_code == 200:
                    cleaned_text = self.clean_html(response.text)
                    # Save snapshot to raw_cache/
                    with open(cache_path, "w", encoding="utf-8") as f:
                        f.write(f"SOURCE_URL: {url}\n{'=' * 40}\n{cleaned_text}")
                    return cleaned_text
                else:
                    logger.warning(f"[HTTP {response.status_code}] Failed to fetch {url}")

            except Exception as e:
                logger.error(f"[FETCH ERROR] Attempt {attempt} failed for {url}: {e}")
                time.sleep(2 * attempt)

        logger.error(f"[ABORT] Exhausted retries for URL: {url}")
        return ""