from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

ROOT_DIR = Path(os.getenv("PROJECT_ROOT", PROJECT_ROOT)).resolve()
KAGGLE_DATASET_SLUG = os.getenv("KAGGLE_DATASET_SLUG", "yasserh/titanic-dataset")
SOURCE_CSV_NAME = os.getenv("SOURCE_CSV_NAME", "Titanic-Dataset.csv")
POSTGRES_CONN_ID = os.getenv("POSTGRES_CONN_ID", "airflow_pipeline_postgres")

DOWNLOAD_DIR = ROOT_DIR / os.getenv("DOWNLOAD_DIR", "data/downloads")
RAW_DIR = ROOT_DIR / os.getenv("RAW_DIR", "data/raw")
PROCESSED_DIR = ROOT_DIR / os.getenv("PROCESSED_DIR", "data/processed")
SUMMARY_DIR = ROOT_DIR / os.getenv("SUMMARY_DIR", "data/summary")
SQL_DIR = ROOT_DIR / "sql"

RAW_CSV_PATH = RAW_DIR / SOURCE_CSV_NAME
PROCESSED_CSV_PATH = PROCESSED_DIR / "titanic_processed.csv"
SUMMARY_JSON_PATH = SUMMARY_DIR / "dataset_summary.json"
CREATE_TABLES_SQL_PATH = SQL_DIR / "create_tables.sql"


def create_directories() -> None:
    for directory in (DOWNLOAD_DIR, RAW_DIR, PROCESSED_DIR, SUMMARY_DIR):
        directory.mkdir(parents=True, exist_ok=True)