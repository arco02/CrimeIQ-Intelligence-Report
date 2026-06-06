from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

# =========================
# BASE
# =========================

BASE_DIR = Path(__file__).resolve().parent.parent

# =========================
# APP
# =========================

APP_NAME = os.getenv(
    "APP_NAME",
    "CrimeIQ"
)

DEBUG = os.getenv(
    "DEBUG",
    "True"
) == "True"

# =========================
# DATABASE
# =========================

DATABASE_URL = os.getenv("DATABASE_URL")

# =========================
# GROQ
# =========================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

MODEL_NAME = os.getenv(
    "MODEL_NAME",
    "llama-3.3-70b-versatile"
)

# =========================
# EMBEDDINGS
# =========================

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "all-MiniLM-L6-v2"
)

EMBEDDING_DIMENSION = 384

# =========================
# DATASETS
# =========================

RAW_DATA_DIR = (
    BASE_DIR /
    "data" /
    "raw"
)

PROCESSED_DATA_DIR = (
    BASE_DIR /
    "data" /
    "processed"
)

CRP_DATASET_PATH = (
    RAW_DATA_DIR /
    "crp.xlsx"
)

PROCESSED_DATASET_PATH = (
    PROCESSED_DATA_DIR /
    "new_dataset.xlsx"
)

# =========================
# MODELS
# =========================

MODELS_DIR = (
    BASE_DIR /
    "data" /
    "models"
)

MODELS_DIR.mkdir(
    parents=True,
    exist_ok=True
)

# =========================
# REPORTS
# =========================

REPORTS_DIR = (
    BASE_DIR /
    "generated_reports"
)

REPORTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)

# =========================
# VECTOR SEARCH
# =========================

TOP_K_VECTOR_RESULTS = 5

# =========================
# FORECASTING
# =========================

FORECAST_YEARS_DEFAULT = 5

MIN_FORECAST_POINTS = 5