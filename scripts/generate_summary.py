from __future__ import annotations

import json
from datetime import datetime, timezone
import pandas as pd

from scripts.common import PROCESSED_CSV_PATH, SUMMARY_JSON_PATH, create_directories


def generate_summary() -> str:

    if not PROCESSED_CSV_PATH.exists():
        raise FileNotFoundError(f"Processed file not found: {PROCESSED_CSV_PATH}")

    dataframe = pd.read_csv(PROCESSED_CSV_PATH)

    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "total_rows": int(len(dataframe)),
        "total_columns": int(len(dataframe.columns)),
        "duplicate_passenger_ids": int(dataframe["passenger_id"].duplicated().sum()),
        "missing_values": int(dataframe.isna().sum().sum()),
        "survived_count": int(dataframe["survived"].sum()),
        "survival_rate": float(dataframe["survived"].mean()),
        "average_age": float(dataframe["age"].mean()),
        "average_fare": float(dataframe["fare"].mean()),
        "first_class_count": int((dataframe["passenger_class"] == 1).sum()),
        "second_class_count": int((dataframe["passenger_class"] == 2).sum()),
        "third_class_count": int((dataframe["passenger_class"] == 3).sum()),
    }

    with SUMMARY_JSON_PATH.open("w", encoding="utf-8") as summary_file:
        json.dump(summary, summary_file, indent=2)

    print(f"Summary generated: {SUMMARY_JSON_PATH}")
    return str(SUMMARY_JSON_PATH)


if __name__ == "__main__":
    generate_summary()