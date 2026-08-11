import os
import pandas as pd
from config import DEFAULT_CONFIG, DATA_DIR
from src.usnews_scraper import USNewsScraper


def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    print("==========================================")
    print(" Phase 1: US News Scraper Starting... ")
    print("==========================================")

    scraper = USNewsScraper(
        subject=DEFAULT_CONFIG["subject"], max_rank=DEFAULT_CONFIG["max_rank"]
    )

    df = scraper.scrape()

    if not df.empty:
        output_path = os.path.join(DATA_DIR, DEFAULT_CONFIG["output_filename"])
        df.to_csv(output_path, index=False, encoding="utf-8-sig")
        print("------------------------------------------")
        print(f"[SUCCESS] Successfully scraped {len(df)} schools.")
        print(f"[OUTPUT] Saved to: {output_path}")
        print("------------------------------------------")
        print(df.head(10))
    else:
        print("[ERROR] Scraper finished, but no data was extracted.")


if __name__ == "__main__":
    main()