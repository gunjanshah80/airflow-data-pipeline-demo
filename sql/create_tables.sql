CREATE SCHEMA IF NOT EXISTS airflow_pipeline_demo;

CREATE TABLE IF NOT EXISTS airflow_pipeline_demo.titanic_passengers (
    passenger_id       INTEGER PRIMARY KEY,
    survived           INTEGER NOT NULL,
    passenger_class    INTEGER NOT NULL,
    name               TEXT NOT NULL,
    sex                VARCHAR(20),
    age                NUMERIC(6, 2),
    siblings_spouses   INTEGER,
    parents_children   INTEGER,
    ticket             TEXT,
    fare               NUMERIC(10, 2),
    cabin              TEXT,
    embarked           VARCHAR(20),
    family_size        INTEGER,
    is_alone           INTEGER,
    age_group          VARCHAR(30),
    loaded_at          TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS airflow_pipeline_demo.dataset_summary (
    run_id                   VARCHAR(250) PRIMARY KEY,
    generated_at_utc         TIMESTAMPTZ NOT NULL,
    total_rows               INTEGER NOT NULL,
    total_columns            INTEGER NOT NULL,
    duplicate_passenger_ids  INTEGER NOT NULL,
    missing_values           INTEGER NOT NULL,
    survived_count           INTEGER NOT NULL,
    survival_rate            NUMERIC(10, 6),
    average_age              NUMERIC(10, 4),
    average_fare             NUMERIC(12, 4),
    first_class_count        INTEGER,
    second_class_count       INTEGER,
    third_class_count        INTEGER,
    loaded_at                TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS airflow_pipeline_demo.etl_audit (
    audit_id          BIGSERIAL PRIMARY KEY,
    run_id            VARCHAR(250) NOT NULL,
    dag_id            VARCHAR(250) NOT NULL,
    task_name         VARCHAR(100) NOT NULL,
    status            VARCHAR(30) NOT NULL,
    rows_processed    INTEGER,
    message           TEXT,
    recorded_at       TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_titanic_survived
    ON airflow_pipeline_demo.titanic_passengers (survived);

CREATE INDEX IF NOT EXISTS idx_titanic_passenger_class
    ON airflow_pipeline_demo.titanic_passengers (passenger_class);

CREATE INDEX IF NOT EXISTS idx_audit_run_id
    ON airflow_pipeline_demo.etl_audit (run_id);