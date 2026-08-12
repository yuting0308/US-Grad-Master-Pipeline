import os
import pandas as pd
from dotenv import load_dotenv

# 載入 .env 環境變數
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
    print(" Phase 2 & 3: URL Discovery & LLM Extraction (Full Top 50) ")
    print("==========================================")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("[WARN] GEMINI_API_KEY not found in environment. Please check your .env file.")
        return

    url_finder = URLFinder()
    extractor = GeminiExtractor(api_key=api_key)

    admissions_urls, handbook_urls = [], []
    toefl_overalls, toefl_speakings, gre_statuses, non_thesis_options, notes_list = [], [], [], [], []

    total_schools = len(df)
    for i, (_, row) in enumerate(df.iterrows(), start=1):
        school_name = row["school_name"]
        print(f"\n[{i}/{total_schools}] Processing: {school_name}...")

        # Phase 2: Find URLs
        found_urls = url_finder.find_urls_for_school(
            school_name, subject="Computer Science"
        )
        adm_url = found_urls["admissions_url"]
        hb_url = found_urls["handbook_url"]

        admissions_urls.append(adm_url)
        handbook_urls.append(hb_url)

        # Phase 3: Gemini LLM Extraction
        extracted = extractor.extract_admission_and_handbook_info(
            school_name=school_name,
            admissions_url=adm_url,
            handbook_url=hb_url,
        )

        toefl_overalls.append(extracted.get("toefl_overall"))
        toefl_speakings.append(extracted.get("toefl_speaking"))
        gre_statuses.append(extracted.get("gre_status"))
        non_thesis_options.append(extracted.get("non_thesis_option"))
        notes_list.append(extracted.get("notes"))

    # Enrich DataFrame
    df["admissions_url"] = admissions_urls
    df["handbook_url"] = handbook_urls
    df["toefl_overall"] = toefl_overalls
    df["toefl_speaking"] = toefl_speakings
    df["gre_status"] = gre_statuses
    df["non_thesis_option"] = non_thesis_options
    df["notes"] = notes_list

    print("\n==========================================")
    print(" Phase 4: Exporting Final Reports ")
    print("==========================================")

    # Export to CSV
    final_csv = os.path.join(DATA_DIR, "usnews_cs_top50_final.csv")
    df.to_csv(final_csv, index=False, encoding="utf-8-sig")
    print(f"[SUCCESS] Final CSV Dataset Saved: {final_csv}")

    # Export to Excel (.xlsx) with formatting
    final_excel = os.path.join(DATA_DIR, "usnews_cs_top50_final.xlsx")
    with pd.ExcelWriter(final_excel, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Top 50 CS Master Programs", index=False)
    print(f"[SUCCESS] Final Excel Report Saved: {final_excel}")

    print("\n==========================================")
    print(" ALL PIPELINE PHASES COMPLETED SUCCESSFULLY! ")
    print("==========================================")


if __name__ == "__main__":
    main()