import os
import sys
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any
from google import genai
from google.genai import types

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.schemas import ProgramRequirementSchema
from src.cleaner import WebContentCleaner

logger = logging.getLogger(__name__)


class GeminiExtractor:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is missing.")

        self.client = genai.Client(api_key=self.api_key)
        self.cleaner = WebContentCleaner(cache_dir="raw_cache", max_chars=12000)

    def extract_program_requirements(
        self,
        university_name: str,
        program_name: str,
        program_category: str,
        admissions_url: str,
        handbook_url: str = "",
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """Extract strictly typed program requirements using Gemini Structured Outputs."""
        logger.info(f"[EXTRACT] Processing: {university_name} - {program_name}")

        admissions_text = self.cleaner.fetch_and_clean(admissions_url, use_cache=use_cache)
        handbook_text = (
            self.cleaner.fetch_and_clean(handbook_url, use_cache=use_cache)
            if handbook_url
            else ""
        )

        combined_text = f"""
        === Admissions Page Content ===
        {admissions_text}

        === Curriculum / Handbook Page Content ===
        {handbook_text}
        """

        prompt = f"""
        You are an academic admissions data engineer extracting structured requirements for:
        - University: {university_name}
        - Program: {program_name}
        - Category: {program_category}
        - Primary Source URL: {admissions_url}

        CRITICAL ANTI-HALLUCINATION RULES:
        1. Extract ONLY facts explicitly stated in the provided text.
        2. Do NOT guess, infer, or fill in default values from outside knowledge.
        3. If GPA minimum, TOEFL minimum, or deadlines are not explicitly mentioned in the text, return null.
        4. If STEM designation is not explicitly confirmed in the text, return null.
        5. Standardize deadlines to YYYY-MM-DD format if year/month/day are clear; otherwise return null.
        6. Set `source_url` to "{admissions_url}".

        Raw Website Content:
        {combined_text[:20000]}
        """

        candidate_models = [
            "models/gemini-flash-latest",
            "models/gemini-3.5-flash",
        ]

        today_str = datetime.now().strftime("%Y-%m-%d")

        for model_name in candidate_models:
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    time.sleep(3)  # Prevent API rate limit bursts

                    response = self.client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=ProgramRequirementSchema,
                            temperature=0.0,
                        ),
                    )

                    parsed_data = json.loads(response.text)
                    # Enforce exact metadata fields
                    parsed_data["university_name"] = university_name
                    parsed_data["program_name"] = program_name
                    parsed_data["program_category"] = program_category
                    parsed_data["source_url"] = admissions_url
                    parsed_data["last_updated"] = today_str
                    return parsed_data

                except Exception as e:
                    err_str = str(e)
                    if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                        logger.warning(
                            f"[RATE LIMIT] Hit 429 on {model_name} (Attempt {attempt+1}/{max_retries}). Sleeping 20s..."
                        )
                        time.sleep(20)
                    else:
                        logger.warning(f"[MODEL ERROR] {model_name} failed: {e}")
                        break

        logger.error(f"[FAILED] Extraction failed for {university_name} - {program_name}")
        fallback_obj = ProgramRequirementSchema(
            university_name=university_name,
            program_name=program_name,
            program_category=program_category,
            is_stem_designated=None,
            thesis_required="Not Specified",
            gpa_minimum=None,
            toefl_minimum=None,
            toefl_notes=None,
            gre_policy="Not Specified",
            prerequisites=[],
            source_url=admissions_url,
            last_updated=today_str,
        )
        return fallback_obj.model_dump()