from __future__ import annotations

import shutil
import zipfile

from scripts.common import (
    DOWNLOAD_DIR,
    RAW_CSV_PATH,
    RAW_DIR,
    SOURCE_CSV_NAME
)

def extract_dataset() -> str:

    zip_files = sorted(
        DOWNLOAD_DIR.glob("*.zip"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )

    if not zip_files:
        raise FileNotFoundError(f"No ZIP file found in {DOWNLOAD_DIR}")

    with zipfile.ZipFile(zip_files[0], "r") as zip_file:
        zip_file.extractall(RAW_DIR)

    extracted_source = RAW_DIR / SOURCE_CSV_NAME

    if not extracted_source.exists():
        csv_files = list(RAW_DIR.rglob("*.csv"))
        if len(csv_files) != 1:
            raise FileNotFoundError(
                f"Could not uniquely identify source CSV. Found: {csv_files}"
            )
        shutil.move(str(csv_files[0]), str(RAW_CSV_PATH))

    if not RAW_CSV_PATH.exists():
        raise FileNotFoundError(f"Expected CSV not found: {RAW_CSV_PATH}")

    print(f"Dataset extracted: {RAW_CSV_PATH}")
    return str(RAW_CSV_PATH)


if __name__ == "__main__":
    extract_dataset()