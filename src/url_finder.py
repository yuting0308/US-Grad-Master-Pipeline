import re
import sys
import os
import time
from typing import Dict, Optional
from urllib.parse import unquote, quote
from bs4 import BeautifulSoup
from curl_cffi import requests as curl_requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class URLFinder:
    def __init__(self):
        self.headers = {
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://html.duckduckgo.com/",
        }

    def search_duckduckgo(self, query: str) -> list[str]:
        """Search DuckDuckGo HTML version to retrieve top search result URLs."""
        search_url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
        urls = []

        try:
            response = curl_requests.get(
                search_url,
                impersonate="chrome120",
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                links = soup.select("a.result__url")
                
                for link in links:
                    raw_href = link.get("href", "")
                    # Extract clean target URL from DuckDuckGo redirect wrapper
                    match = re.search(r"uddg=([^&]+)", raw_href)
                    if match:
                        clean_url = unquote(match.group(1))
                        urls.append(clean_url)
                    elif raw_href.startswith("http"):
                        urls.append(raw_href)

        except Exception as e:
            print(f"[WARN] DuckDuckGo search failed for query '{query}': {e}")

        return urls

    def find_urls_for_school(self, school_name: str, subject: str = "Computer Science") -> Dict[str, Optional[str]]:
        """Find direct Admissions and Student Handbook URLs for a given university."""
        print(f"[INFO] Locating URLs for: {school_name}...")

        # Query 1: Admissions Page Search
        admissions_query = f"{school_name} {subject} master graduate admission requirements"
        admissions_results = self.search_duckduckgo(admissions_query)
        admissions_url = self._pick_best_admissions_url(admissions_results, school_name)
        
        time.sleep(1.5)  # Rate limit prevention

        # Query 2: Student Handbook / Degree Requirements Search
        handbook_query = f"{school_name} {subject} graduate student handbook degree requirements pdf"
        handbook_results = self.search_duckduckgo(handbook_query)
        handbook_url = self._pick_best_handbook_url(handbook_results, school_name)

        return {
            "admissions_url": admissions_url,
            "handbook_url": handbook_url
        }

    def _pick_best_admissions_url(self, urls: list[str], school_name: str) -> Optional[str]:
        """Rank and pick the best matching admissions URL."""
        keywords = ["admission", "apply", "requirement", "prospective", "graduate"]
        for url in urls:
            url_lower = url.lower()
            if any(kw in url_lower for kw in keywords):
                return url
        return urls[0] if urls else None

    def _pick_best_handbook_url(self, urls: list[str], school_name: str) -> Optional[str]:
        """Rank and pick the best matching student handbook URL (preferring PDFs or handbook paths)."""
        # Prioritize direct PDF links or URLs with handbook/degree requirements
        for url in urls:
            url_lower = url.lower()
            if "handbook" in url_lower or "degree-requirement" in url_lower or url_lower.endswith(".pdf"):
                return url
        
        keywords = ["curriculum", "academics", "program", "master"]
        for url in urls:
            url_lower = url.lower()
            if any(kw in url_lower for kw in keywords):
                return url

        return urls[0] if urls else None