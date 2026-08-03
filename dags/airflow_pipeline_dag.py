"""
Apache Airflow DAG for the Kaggle Titanic ETL pipeline.

Pipeline flow:

download_dataset
        ↓
extract_dataset
        ↓
transform_dataset
       ↙ ↘
generate_summary   create_tables
       ↘            ↙
         load_postgres
                ↓
           verify_load
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta

from airflow.sdk import dag, task, get_current_context

from pipeline_scripts.create_db_tables import create_tables
from scripts.download_dataset import download_dataset
from scripts.extract_dataset import extract_dataset
from scripts.generate_summary import generate_summary
from pipeline_scripts.load_postgres import load_to_postgres
from scripts.transform_data import transform_dataset
from pipeline_scripts.verify_load import verify_postgres_load


LOGGER = logging.getLogger(__name__)


DEFAULT_ARGS = {
    "owner": "Gunjan",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}

@dag(
    dag_id="titanic_data_pipeline",
    description="Download Titanic data from Kaggle, transform it and load it into PostgreSQL",
    default_args=DEFAULT_ARGS,
    start_date=datetime(2026, 7, 1),
    schedule=None,
    catchup=False,
    max_active_runs=1,
    tags=["kaggle", "titanic", "etl", "postgres"],
)
def airflow_pipeline() -> None:
    """
    Define the complete Titanic ETL workflow.
    """

    @task(task_id="generate_pipeline_run_id")
    def generate_pipeline_run_id() -> str:
        return str(uuid.uuid4())

    @task(task_id="download_dataset")
    def download_dataset_task() -> str:
        """
        Download the Titanic dataset ZIP file from Kaggle.

        Returns:
            Path of the downloaded ZIP file.
        """
        LOGGER.info("Starting Kaggle dataset download")

        downloaded_file = download_dataset()

        LOGGER.info(
            "Dataset downloaded successfully: %s",
            downloaded_file,
        )

        return str(downloaded_file)

    @task(task_id="extract_dataset")
    def extract_dataset_task(downloaded_file: str) -> str:
        """
        Extract the downloaded dataset.

        Args:
            downloaded_file: Path returned by the download task.

        Returns:
            Path of the extracted CSV file.
        """
        LOGGER.info(
            "Starting dataset extraction from: %s",
            downloaded_file,
        )

        extracted_file = extract_dataset()

        LOGGER.info(
            "Dataset extracted successfully: %s",
            extracted_file,
        )

        return str(extracted_file)

    @task(task_id="transform_dataset")
    def transform_dataset_task(extracted_file: str) -> str:
        """
        Clean and transform the extracted Titanic dataset.

        Args:
            extracted_file: Path of the extracted raw CSV file.

        Returns:
            Path of the transformed CSV file.
        """
        LOGGER.info(
            "Starting transformation for: %s",
            extracted_file,
        )

        transformed_file = transform_dataset()

        LOGGER.info(
            "Dataset transformed successfully: %s",
            transformed_file,
        )

        return str(transformed_file)

    @task(task_id="generate_summary")
    def generate_summary_task(transformed_file: str) -> str:
        """
        Generate summary statistics from the transformed dataset.

        Args:
            transformed_file: Path of the transformed CSV file.

        Returns:
            Path of the generated summary file.
        """
        LOGGER.info(
            "Generating summary from: %s",
            transformed_file,
        )

        summary_file = generate_summary()

        LOGGER.info(
            "Summary generated successfully: %s",
            summary_file,
        )

        return str(summary_file)

    @task(task_id="create_postgres_tables")
    def create_tables_task() -> None:
        """
        Create the required PostgreSQL tables.
        """
        LOGGER.info("Creating PostgreSQL tables")

        create_tables()

        LOGGER.info("PostgreSQL tables created successfully")

    @task(task_id="load_postgres")
    def load_postgres_task(
            run_id: str,
            transformed_file: str,
            summary_file: str
    ) -> None:
        """
        Load transformed and summary data into PostgreSQL.

        Args:
            transformed_file: Path of the transformed dataset.
            summary_file: Path of the generated summary data.
        """
        LOGGER.info(
            "Loading transformed data into PostgreSQL: %s",
            transformed_file,
        )

        LOGGER.info(
            "Loading summary data into PostgreSQL: %s",
            summary_file,
        )

        load_to_postgres(
            run_id=run_id
        )

        LOGGER.info("PostgreSQL load completed successfully")

    @task(task_id="verify_postgres_load")
    def verify_load_task(run_id: str) -> None:
        """
        Verify that PostgreSQL tables contain the expected records.
        """
        LOGGER.info("Starting PostgreSQL load verification")

        verification_result = verify_postgres_load(
            run_id=run_id
        )

        if verification_result is False:
            raise ValueError(
                "PostgreSQL data verification failed"
            )

        LOGGER.info(
            "PostgreSQL data verification completed successfully"
        )

    pipeline_run_id = generate_pipeline_run_id()

    downloaded_file = download_dataset_task()

    extracted_file = extract_dataset_task(
        downloaded_file
    )

    transformed_file = transform_dataset_task(
        extracted_file
    )

    summary_file = generate_summary_task(
        transformed_file
    )

    tables_created = create_tables_task()

    load_task = load_postgres_task(
        run_id=pipeline_run_id,
        transformed_file=transformed_file,
        summary_file=summary_file,
    )

    verification_task = verify_load_task(
        run_id=pipeline_run_id
    )



airflow_pipeline()