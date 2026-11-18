import os
import json
import logging
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

from src.llm_extractor import GeminiExtractor

logger = logging.getLogger(__name__)

TARGETS_PATH = os.path.join("data", "targets.json")
OUTPUT_JSON_PATH = os.path.join("data", "programs_data.json")
OUTPUT_CSV_PATH = os.path.join("data", "programs_summary.csv")


def load_existing_records(json_path: str) -> dict:
    """Load existing extracted records indexed by (university_name, program_name)."""
    if not os.path.exists(json_path):
        return {}
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            records = json.load(f)
        return {
            (item["university_name"], item["program_name"]): item
            for item in records
            if "university_name" in item and "program_name" in item
        }
    except Exception as e:
        logger.warning(f"[WARN] Could not load existing JSON records: {e}")
        return {}


def export_flattened_csv(records: list, csv_path: str):
    """Flatten nested JSON fields (prerequisites, deadlines) into a clean summary CSV."""
    flattened_rows = []
    for rec in records:
        deadlines = rec.get("application_deadlines") or {}
        prereqs = rec.get("prerequisites") or []
        flattened_rows.append(
            {
                "university_name": rec.get("university_name"),
                "program_name": rec.get("program_name"),
                "program_category": rec.get("program_category"),
                "is_stem_designated": rec.get("is_stem_designated"),
                "thesis_required": rec.get("thesis_required"),
                "gpa_minimum": rec.get("gpa_minimum"),
                "toefl_minimum": rec.get("toefl_minimum"),
                "toefl_notes": rec.get("toefl_notes"),
                "gre_policy": rec.get("gre_policy"),
                "prerequisites": "; ".join(prereqs) if prereqs else "None Listed",
                "priority_deadline": deadlines.get("priority_deadline"),
                "final_deadline": deadlines.get("final_deadline"),
                "source_url": rec.get("source_url"),
                "last_updated": rec.get("last_updated"),
            }
        )

    df = pd.DataFrame(flattened_rows)
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")


def main():
    os.makedirs("data", exist_ok=True)

    if not os.path.exists(TARGETS_PATH):
        logger.error(f"[ERROR] Target config file not found: {TARGETS_PATH}")
        return

    with open(TARGETS_PATH, "r", encoding="utf-8") as f:
        targets = json.load(f)

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("[ERROR] GEMINI_API_KEY not found in .env file.")
        return

    extractor = GeminiExtractor(api_key=api_key)
    records_map = load_existing_records(OUTPUT_JSON_PATH)

    total = len(targets)
    logger.info(f"Starting US-Grad-Master-Pipeline for {total} target programs...")

    for idx, target in enumerate(targets, start=1):
        univ = target["university_name"]
        prog = target["program_name"]
        cat = target.get("program_category", "Other")
        adm_url = target["admissions_url"]
        hb_url = target.get("handbook_url", "")

        logger.info(f"[{idx}/{total}] Processing: {univ} | {prog} ({cat})")

        extracted_record = extractor.extract_program_requirements(
            university_name=univ,
            program_name=prog,
            program_category=cat,
            admissions_url=adm_url,
            handbook_url=hb_url,
            use_cache=True,
        )

        # Upsert using composite unique key (university_name, program_name)
        records_map[(univ, prog)] = extracted_record

    final_records = list(records_map.values())

    # 1. Export nested structured JSON
    with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(final_records, f, indent=2, ensure_ascii=False)
    logger.info(f"[SUCCESS] Saved structured JSON dataset to: {OUTPUT_JSON_PATH}")

    # 2. Export flattened summary CSV
    export_flattened_csv(final_records, OUTPUT_CSV_PATH)
    logger.info(f"[SUCCESS] Saved flattened CSV summary to: {OUTPUT_CSV_PATH}")


if __name__ == "__main__":
    main()