from __future__ import annotations

import json
from datetime import datetime, timezone
import pandas as pd
from airflow.providers.postgres.hooks.postgres import PostgresHook

from scripts.common import POSTGRES_CONN_ID, PROCESSED_CSV_PATH, SUMMARY_JSON_PATH

PASSENGER_COLUMNS = [
    "passenger_id", "survived", "passenger_class", "name", "sex", "age",
    "siblings_spouses", "parents_children", "ticket", "fare", "cabin",
    "embarked", "family_size", "is_alone", "age_group",
]


def load_to_postgres(run_id) -> int:
    dataframe = pd.read_csv(PROCESSED_CSV_PATH)

    with SUMMARY_JSON_PATH.open("r", encoding="utf-8") as summary_file:
        summary = json.load(summary_file)

    postgres_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
    engine = postgres_hook.get_sqlalchemy_engine()

    with engine.begin() as connection:
        connection.exec_driver_sql("TRUNCATE TABLE airflow_pipeline_demo.titanic_passengers")

        dataframe[PASSENGER_COLUMNS].to_sql(
            name="titanic_passengers",
            schema="airflow_pipeline_demo",
            con=connection,
            if_exists="append",
            index=False,
            method="multi",
            chunksize=500,
        )

        connection.exec_driver_sql(
            "DELETE FROM airflow_pipeline_demo.dataset_summary WHERE run_id = %(run_id)s",
            {"run_id": run_id},
        )

        connection.exec_driver_sql(
            """
            INSERT INTO airflow_pipeline_demo.dataset_summary (
                run_id, generated_at_utc, total_rows, total_columns,
                duplicate_passenger_ids, missing_values, survived_count,
                survival_rate, average_age, average_fare,
                first_class_count, second_class_count, third_class_count
            ) VALUES (
                %(run_id)s, %(generated_at_utc)s, %(total_rows)s,
                %(total_columns)s, %(duplicate_passenger_ids)s,
                %(missing_values)s, %(survived_count)s, %(survival_rate)s,
                %(average_age)s, %(average_fare)s, %(first_class_count)s,
                %(second_class_count)s, %(third_class_count)s
            )
            """,
            {"run_id": run_id, **summary},
        )

        connection.exec_driver_sql(
            """
            INSERT INTO airflow_pipeline_demo.etl_audit (
                run_id, dag_id, task_name, status,
                rows_processed, message, recorded_at
            ) VALUES (
                %(run_id)s, 'kaggle_postgres_etl', 'load_to_postgres',
                'SUCCESS', %(rows_processed)s,
                'Passenger and summary data loaded successfully',
                %(recorded_at)s
            )
            """,
            {
                "run_id": run_id,
                "rows_processed": len(dataframe),
                "recorded_at": datetime.now(timezone.utc),
            },
        )

    print(f"Loaded {len(dataframe)} passenger records for run {run_id}")
    return int(len(dataframe))


if __name__ == "__main__":
    load_to_postgres(run_id='manual_test_run')