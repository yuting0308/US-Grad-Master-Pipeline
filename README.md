# 🎓 US Graduate Master\'s Admissions & Graduation Requirements Automated Data Pipeline

An automated data pipeline designed to streamline the graduate school selection process for applicants in Computer Science, Data Science, and Engineering. The pipeline scrapes top US university master\'s program rankings, dynamically locates program admissions pages and student handbooks, and extracts key degree requirements (such as TOEFL/GRE thresholds and non-thesis options) using Google Gemini LLM.

---

## 💡 Problem Statement

* **Time-Consuming Research:** Prospective students manually review dozens of university websites to verify admission criteria and language proficiency requirements.
* **Complex Graduation Criteria:** Identifying whether a program offers a course-based (non-thesis) track often requires downloading and reading lengthy PDF student handbooks.
* **Automated Solution:** This project builds an end-to-end automated data pipeline combining web scrapers, URL discovery algorithms, LLM text extraction, and scheduled reporting.

---

## 🛠 Tech Stack

* **Core Language:** Python 3.10+
* **Data Scraping & TLS Impersonation:** \curl_cffi\, \BeautifulSoup4\, \Playwright* **Data Processing & Export:** \pandas\, \openpyxl* **AI Extraction Engine:** Google Gemini API (\google-genai\ SDK)
* **CI/CD & Scheduled Workflows:** GitHub Actions

---

## 🏗 Pipeline Architecture & System Workflow

\\	ext
[US News Ranking Scraper]
         │
         ▼
[Admissions & Handbook URL Discovery]
         │
         ▼
[Webpage / PDF Text Extractor]
         │
         ▼
[Gemini LLM Structuring Engine] ──> [Structured CSV/Excel Report]
                                             ▲
                                             │
                                   [GitHub Actions Scheduler]
\
1. **Phase 1: US News Scraper (Data Acquisition)**
   * Scrapes university rankings across target domains (Computer Science, Engineering, Mathematics).
   * Implements TLS fingerprint impersonation (\curl_cffi\) and dynamic fallback mechanisms to handle Cloudflare anti-bot mechanisms.
2. **Phase 2: Admissions & Handbook URL Finder (URL Discovery)**
   * Dynamically searches and resolves direct links to Graduate Admissions pages and Student Handbook documents (PDF/HTML).
3. **Phase 3: AI Threshold Extractor (Information Extraction)**
   * Feeds raw webpage text or PDF content into Gemini Flash LLM to extract structured fields:
     * TOEFL / IELTS overall score and sub-score cutoffs.
     * GRE requirement status (Required / Optional / Waived).
     * Non-Thesis / Coursework-only options (Yes / No).
4. **Phase 4 & 5: Export & Cloud Automation**
   * Consolidates structured metrics into clean Excel (\.xlsx\) and CSV reports.
   * Runs automated periodic executions via GitHub Actions.

---

## 📂 Project Directory Structure

\\	ext
US-Grad-Master-Pipeline/
├── .gitignore
├── config.py             # Global pipeline configuration and domain mappings
├── main.py               # Main pipeline execution entry point
├── requirements.txt      # Project dependencies
├── README.md             # Project documentation
├── data/                 # Exported data reports (CSV/Excel)
└── src/
    ├── __init__.py
    └── usnews_scraper.py # Phase 1 ranking scraper module
\
---

## 🚀 Quick Start

### Prerequisites

* Python 3.10 or higher
* Git

### Installation

1. **Clone the repository:**
   \\ash
   git clone https://github.com/YOUR_USERNAME/US-Grad-Master-Pipeline.git
   cd US-Grad-Master-Pipeline
   \
2. **Set up a virtual environment:**
   \\ash
   python -m venv venv

   # On macOS / Linux:
   source venv/bin/activate

   # On Windows (PowerShell):
   .\venv\Scripts\Activate.ps1
   \
3. **Install dependencies:**
   \\ash
   pip install -r requirements.txt
   \
4. **Run Phase 1 Scraper:**
   \\ash
   python main.py
   \
---

## 📊 Sample Output Schema

| School Name | US News Rank | TOEFL Overall | TOEFL Speaking | GRE Status | Non-Thesis Option | Admissions URL |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Carnegie Mellon University | #1 | 100 | >= 22 | Optional | Yes | [Link](https://www.cmu.edu) |
| Stanford University | #1 | 89 | N/A | Not Required | Yes | [Link](https://www.stanford.edu) |

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).
