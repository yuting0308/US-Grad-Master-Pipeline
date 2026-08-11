import os
import re
import sys
import time
import pandas as pd
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import TARGET_SUBJECTS, DATA_DIR


class USNewsScraper:
    def __init__(self, subject: str = "cs", max_rank: int = 50):
        self.subject = subject.lower()
        self.max_rank = max_rank
        self.base_url = TARGET_SUBJECTS.get(self.subject)

        if not self.base_url:
            raise ValueError(
                f"Unsupported subject: {subject}. Valid options: {list(TARGET_SUBJECTS.keys())}"
            )

    def scrape(self) -> pd.DataFrame:
        """Main scraping loop returning a pandas DataFrame with university rankings."""
        results = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                viewport={"width": 1280, "height": 800},
            )
            page = context.new_page()

            current_page = 1
            while True:
                url = (
                    f"{self.base_url}/page/{current_page}"
                    if current_page > 1
                    else self.base_url
                )
                print(f"[INFO] Fetching page {current_page}: {url}")

                try:
                    page.goto(url, wait_until="networkidle", timeout=30000)
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    time.sleep(2)
                except Exception as e:
                    print(f"[WARN] Page load timeout or error: {e}")
                    break

                soup = BeautifulSoup(page.content(), "html.parser")
                schools_on_page = self._parse_page(soup)

                if not schools_on_page:
                    print("[INFO] No more schools found or end of list reached.")
                    break

                for school in schools_on_page:
                    if school["rank"] is not None and school["rank"] > self.max_rank:
                        print(
                            f"[INFO] Reached max rank limit ({self.max_rank}). Stopping scrape."
                        )
                        browser.close()
                        return pd.DataFrame(results)
                    results.append(school)

                current_page += 1

            browser.close()

        return pd.DataFrame(results)

    def _parse_page(self, soup: BeautifulSoup) -> list:
        """Parse HTML DOM structure to extract university details."""
        parsed_data = []
        cards = soup.select("div[class*='DetailCard'], div[class*='Card-']")

        if not cards:
            cards = soup.find_all("div", class_=lambda x: x and "card" in x.lower())

        for card in cards:
            name_tag = card.select_one("h2, a[class*='SchoolName'], div[class*='heading']")
            school_name = name_tag.get_text(strip=True) if name_tag else None

            if not school_name:
                continue

            rank_tag = card.select_one("div[class*='Rank'], span[class*='rank']")
            rank_num = None
            if rank_tag:
                rank_str = rank_tag.get_text(strip=True)
                match = re.search(r"#(\d+)", rank_str)
                if match:
                    rank_num = int(match.group(1))

            link_tag = card.select_one("a[href*='/best-graduate-schools/']")
            detail_url = (
                f"https://www.usnews.com{link_tag['href']}"
                if link_tag and link_tag.get("href")
                else None
            )

            parsed_data.append({
                "school_name": school_name,
                "rank": rank_num,
                "detail_url": detail_url,
                "subject": self.subject,
            })

        return parsed_data