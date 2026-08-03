from __future__ import annotations

import subprocess
from pathlib import Path

from scripts.common import DOWNLOAD_DIR, KAGGLE_DATASET_SLUG, create_directories

def download_dataset() -> str:
    create_directories()

    command = [
        "kaggle", "datasets", "download",
        "-d", KAGGLE_DATASET_SLUG,
        "-p", str(DOWNLOAD_DIR),
        "--force",
    ]
    subprocess.run(command, check=True)

    zip_files = sorted(
        DOWNLOAD_DIR.glob("*.zip"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )

    if not zip_files:
        raise FileNotFoundError(f"No ZIP file downloaded into {DOWNLOAD_DIR}")

    downloaded_zip: Path = zip_files[0]
    print(f"Dataset downloaded: {downloaded_zip}")
    return str(downloaded_zip)


if __name__ == "__main__":
    download_dataset()