from pathlib import Path

from airflow.providers.postgres.hooks.postgres import PostgresHook


POSTGRES_CONN_ID = "airflow_pipeline_postgres"

SQL_FILE = (
        Path(__file__).resolve().parents[2]
        / "sql"
        / "create_tables.sql"
)


def create_tables() -> None:
    postgres_hook = PostgresHook(
        postgres_conn_id=POSTGRES_CONN_ID
    )

    sql = SQL_FILE.read_text(encoding="utf-8")
    postgres_hook.run(sql)

    print("Tables created successfully.")


if __name__ == "__main__":
    create_tables()