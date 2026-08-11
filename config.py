import os

# Base directory setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# US News category URLs mapping
TARGET_SUBJECTS = {
    "cs": "https://www.usnews.com/best-graduate-schools/top-science-schools/computer-science-rankings",
    "engineering": "https://www.usnews.com/best-graduate-schools/top-engineering-schools/eng-rankings",
    "math": "https://www.usnews.com/best-graduate-schools/top-science-schools/mathematics-rankings"
}

# Default scraping configuration
DEFAULT_CONFIG = {
    "subject": "cs",
    "max_rank": 50,
    "output_filename": "usnews_cs_top50.csv"
}
