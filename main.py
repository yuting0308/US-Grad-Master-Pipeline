import os
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

from config import DEFAULT_CONFIG, DATA_DIR
from src.usnews_scraper import USNewsScraper
from src.url_finder import URLFinder
from src.llm_extractor import GeminiExtractor


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
    sample_df = df.head(3).copy()  # 先測試前 3 名學校
    admissions_urls = []
    handbook_urls = []

    for _, row in sample_df.iterrows():
        school_name = row["school_name"]
        found_urls = url_finder.find_urls_for_school(
            school_name, subject="Computer Science"
        )
        admissions_urls.append(found_urls["admissions_url"])
        handbook_urls.append(found_urls["handbook_url"])

    sample_df["admissions_url"] = admissions_urls
    sample_df["handbook_url"] = handbook_urls

    print("\n==========================================")
    print(" Phase 3: Gemini LLM Structured Extraction ")
    print("==========================================")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("[WARN] GEMINI_API_KEY not found in environment. Please set it in .env file.")
        return

    extractor = GeminiExtractor(api_key=api_key)

    toefl_overalls, toefl_speakings, gre_statuses, non_thesis_options, notes_list = [], [], [], [], []

    for _, row in sample_df.iterrows():
        extracted = extractor.extract_admission_and_handbook_info(
            school_name=row["school_name"],
            admissions_url=row["admissions_url"],
            handbook_url=row["handbook_url"],
        )

        toefl_overalls.append(extracted.get("toefl_overall"))
        toefl_speakings.append(extracted.get("toefl_speaking"))
        gre_statuses.append(extracted.get("gre_status"))
        non_thesis_options.append(extracted.get("non_thesis_option"))
        notes_list.append(extracted.get("notes"))

    sample_df["toefl_overall"] = toefl_overalls
    sample_df["toefl_speaking"] = toefl_speakings
    sample_df["gre_status"] = gre_statuses
    sample_df["non_thesis_option"] = non_thesis_options
    sample_df["notes"] = notes_list

    final_output_path = os.path.join(DATA_DIR, "usnews_cs_top3_extracted.csv")
    sample_df.to_csv(final_output_path, index=False, encoding="utf-8-sig")

    print("------------------------------------------")
    print(f"[SUCCESS] Phase 3 Complete! Saved to: {final_output_path}")
    print("------------------------------------------")
    print(
        sample_df[
            [
                "school_name",
                "toefl_overall",
                "gre_status",
                "non_thesis_option",
                "notes",
            ]
        ]
    )


if __name__ == "__main__":
    main()