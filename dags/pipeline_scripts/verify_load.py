from __future__ import annotations

import json
import pandas as pd
from airflow.providers.postgres.hooks.postgres import PostgresHook

from scripts.common import POSTGRES_CONN_ID, PROCESSED_CSV_PATH, SUMMARY_JSON_PATH


def verify_postgres_load(run_id: str) -> dict[str, int | str]:
    dataframe = pd.read_csv(PROCESSED_CSV_PATH)

    with SUMMARY_JSON_PATH.open("r", encoding="utf-8") as summary_file:
        expected_summary = json.load(summary_file)

    expected_rows = len(dataframe)
    postgres_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)

    passenger_count = postgres_hook.get_first(
        "SELECT COUNT(*) FROM airflow_pipeline_demo.titanic_passengers"
    )[0]

    summary_row = postgres_hook.get_first(
        """
        SELECT total_rows, missing_values
        FROM airflow_pipeline_demo.dataset_summary
        WHERE run_id = %s
        """,
        parameters=(run_id,),
    )

    if summary_row is None:
        raise ValueError(f"No summary record found for run_id={run_id}")

    database_summary_rows = int(summary_row[0])
    database_missing_values = int(summary_row[1])

    if passenger_count != expected_rows:
        raise ValueError(
            f"Passenger row-count failed: expected={expected_rows}, actual={passenger_count}"
        )

    if database_summary_rows != expected_rows:
        raise ValueError(
            f"Summary row-count failed: expected={expected_rows}, actual={database_summary_rows}"
        )

    if database_missing_values != int(expected_summary["missing_values"]):
        raise ValueError("Missing-value summary verification failed")

    result = {
        "status": "SUCCESS",
        "run_id": run_id,
        "verified_passenger_rows": int(passenger_count),
        "verified_summary_rows": database_summary_rows,
    }

    return result


if __name__ == "__main__":
    verify_postgres_load(run_id="manual_test_run")