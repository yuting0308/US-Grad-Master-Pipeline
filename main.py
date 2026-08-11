import os
import pandas as pd
from config import DEFAULT_CONFIG, DATA_DIR
from src.usnews_scraper import USNewsScraper
from src.url_finder import URLFinder


def main():
    os.makedirs(DATA_DIR, exist_ok=True)

    print("==========================================")
    print(" Phase 1: US News Scraper Starting... ")
    print("==========================================")

    scraper = USNewsScraper(
        subject=DEFAULT_CONFIG["subject"], max_rank=DEFAULT_CONFIG["max_rank"]
    )
    df = scraper.scrape()

    if df.empty:
        print("[ERROR] Scraper finished, but no data was extracted.")
        return

    output_path = os.path.join(DATA_DIR, DEFAULT_CONFIG["output_filename"])
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"[SUCCESS] Phase 1 Complete. Saved to: {output_path}")

    print("\n==========================================")
    print(" Phase 2: Admissions & Handbook URL Discovery ")
    print("==========================================")

    url_finder = URLFinder()
    
    # Process sample schools (e.g., top 5) for Phase 2 validation
    sample_df = df.head(5).copy()
    admissions_urls = []
    handbook_urls = []

    for _, row in sample_df.iterrows():
        school_name = row["school_name"]
        found_urls = url_finder.find_urls_for_school(school_name, subject="Computer Science")
        
        admissions_urls.append(found_urls["admissions_url"])
        handbook_urls.append(found_urls["handbook_url"])

    sample_df["admissions_url"] = admissions_urls
    sample_df["handbook_url"] = handbook_urls

    enriched_output_path = os.path.join(DATA_DIR, "usnews_cs_top50_enriched.csv")
    sample_df.to_csv(enriched_output_path, index=False, encoding="utf-8-sig")

    print("------------------------------------------")
    print(f"[SUCCESS] Phase 2 Sample Complete. Saved to: {enriched_output_path}")
    print("------------------------------------------")
    print(sample_df[["school_name", "admissions_url", "handbook_url"]])


if __name__ == "__main__":
    main()