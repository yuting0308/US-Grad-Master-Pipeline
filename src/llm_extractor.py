import os
import sys
import json
from typing import Dict, Any
from google import genai
from google.genai import types
from curl_cffi import requests as curl_requests
from bs4 import BeautifulSoup

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class GeminiExtractor:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is missing.")
        
        # Initialize official google-genai client
        self.client = genai.Client(api_key=self.api_key)

    def fetch_webpage_text(self, url: str) -> str:
        """Fetch webpage HTML content and clean it into plain text."""
        if not url or not url.startswith("http"):
            return ""

        try:
            response = curl_requests.get(url, impersonate="chrome120", timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                # Remove non-content elements
                for script in soup(["script", "style", "nav", "footer"]):
                    script.extract()
                text = soup.get_text(separator=" ", strip=True)
                return text[:10000]  # Limit context length
        except Exception as e:
            print(f"[WARN] Failed to fetch text from {url}: {e}")

        return ""

    def extract_admission_and_handbook_info(
        self, school_name: str, admissions_url: str, handbook_url: str
    ) -> Dict[str, Any]:
        """Extract structured admission thresholds and graduation requirements via Gemini API."""
        print(f"[INFO] Running Gemini Extraction for: {school_name}...")

        admissions_text = self.fetch_webpage_text(admissions_url)
        handbook_text = self.fetch_webpage_text(handbook_url)

        combined_text = f"""
        === Admissions Content ===
        {admissions_text}

        === Handbook Content ===
        {handbook_text}
        """

        prompt = f"""
        You are an academic advisor parsing graduate admissions and program requirements for {school_name}.
        Analyze the raw text and extract the required fields accurately.

        Output must be a valid JSON object matching this schema:
        {{
            "toefl_overall": "Overall minimum TOEFL score (e.g. '100', '80', 'Not Specified')",
            "toefl_speaking": "Minimum Speaking section score (e.g. '>= 22', 'N/A')",
            "gre_status": "GRE requirement status: MUST be one of ['Required', 'Optional', 'Not Required', 'Waived']",
            "non_thesis_option": "Whether a coursework-only (non-thesis) Master's option is available: MUST be one of ['Yes', 'No', 'Coursework-only']",
            "notes": "Brief key notes (e.g. required credit hours, max 20 words)"
        }}

        Raw Website Content:
        {combined_text[:15000]}
        """

        # Model candidates with full resource prefix based on your API key capability
        candidate_models = [
            "models/gemini-flash-latest",
            "models/gemini-2.5-pro",
            "models/gemini-3.5-flash",
        ]

        for model_name in candidate_models:
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.1,
                    ),
                )

                result_json = json.loads(response.text)
                return result_json

            except Exception as e:
                print(f"[WARN] Model '{model_name}' failed: {e}. Trying next...")
                continue

        print(f"[ERROR] All candidate Gemini models failed for {school_name}.")
        return {
            "toefl_overall": "N/A",
            "toefl_speaking": "N/A",
            "gre_status": "Unknown",
            "non_thesis_option": "Unknown",
            "notes": "Extraction failed.",
        }