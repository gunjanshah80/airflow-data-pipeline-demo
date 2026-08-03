# Apache Airflow ETL Pipeline

A complete local data engineering project that uses **Apache Airflow** to orchestrate ETL pipeline:

```text
Download the dataset from Kaggle
        │
        ▼
Extract the downloaded data
        │
        ▼
Perform the data tranformation
        │
        ▼
Generate the summary/stats
        │
        ▼
Create tables in Postgres DB
        │
        ▼
Load the detailed and summary data into the tables
        │
        ▼
Verify the loaded data
```

The pipeline downloads a public Titanic dataset from Kaggle, extracts and transforms the CSV data, generates summary metrics, creates PostgreSQL tables, loads the processed data and summary, and verifies that the load completed successfully.

## What this project demonstrates

- Workflow orchestration with Apache Airflow
- Programmatic Kaggle dataset downloads
- CSV extraction and Pandas transformations
- PostgreSQL schema and table creation
- Loading cleaned data and summary metrics
- ETL auditing and post-load verification
- Secure configuration using Airflow Connections and environment variables

## Technology stack

- Ubuntu Linux
- Python 3.12
- Apache Airflow 3.x
- PostgreSQL
- Pandas
- SQLAlchemy
- Psycopg
- Kaggle CLI/API

## Dataset

This example uses:

```text
yasserh/titanic-dataset
```

Expected CSV:

```text
Titanic-Dataset.csv
```

## Repository structure

```text
airflow-data-pipeline-demo/
├── dags/
│   └── kaggle_postgres_pipeline.py
├── scripts/
│   ├── __init__.py
│   ├── common.py
│   ├── download_dataset.py
│   ├── extract_dataset.py
│   ├── transform_dataset.py
│   ├── generate_summary.py
│   ├── create_tables.py
│   ├── load_postgres.py
│   └── verify_load.py
├── sql/
│   └── create_tables.sql
├── data/
│   ├── downloads/
│   ├── raw/
│   ├── processed/
│   └── summary/
├── tests/
│   └── test_transform.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

Create it:

```bash
mkdir -p airflow-data-pipeline-demo/{dags,scripts,sql,tests}
mkdir -p airflow-data-pipeline-demo/data/{downloads,raw,processed,summary}
cd airflow-data-pipeline-demo
touch scripts/__init__.py
```

# 1. Prerequisites

- Ubuntu 22.04 or later
- Python 3.12
- PostgreSQL
- Kaggle account
- Git
- Internet access
- At least 4 GB RAM for local Airflow development

Check Python:

```bash
python3.12 --version
```

# 2. Install system packages

```bash
sudo apt update
sudo apt install -y \
  python3.12 \
  python3.12-venv \
  python3-pip \
  postgresql \
  postgresql-contrib \
  libpq-dev \
  build-essential \
  unzip \
  git
```

Start PostgreSQL:

```bash
sudo systemctl enable postgresql
sudo systemctl start postgresql
sudo systemctl status postgresql
```

# 3. Create a virtual environment

```bash
python3.12 -m venv airflow-env
source airflow-env/bin/activate
python -m pip install --upgrade pip setuptools wheel
```

For every new terminal:

```bash
cd airflow-data-pipeline-demo
source airflow-env/bin/activate
```

# 4. Install Apache Airflow and dependencies

Airflow should be installed with its official constraints file.

```bash
export AIRFLOW_VERSION=3.3.0
export PYTHON_VERSION=3.12

CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"

python -m pip install \
  "apache-airflow==${AIRFLOW_VERSION}" \
  --constraint "${CONSTRAINT_URL}"
```

Install the PostgreSQL provider and project packages:

```bash
python -m pip install \
  apache-airflow-providers-postgres \
  pandas \
  sqlalchemy \
  psycopg2-binary \
  kaggle \
  python-dotenv \
  pytest
```

Verify:

```bash
airflow version
python --version
```

## requirements.txt

```text
apache-airflow==3.3.0
apache-airflow-providers-postgres
pandas
sqlalchemy
psycopg2-binary
kaggle
python-dotenv
pytest
```

> For a clean machine, install Airflow with its constraints file first, then install the remaining packages.

# 5. Configure Airflow

```bash
export AIRFLOW_HOME="$HOME/airflow"
export AIRFLOW__CORE__DAGS_FOLDER="$(pwd)/dags"
```

Confirm:

```bash
echo "$AIRFLOW_HOME"
airflow config get-value core dags_folder
```

You may add these exports to `~/.bashrc`, but replace the DAG path with the repository’s absolute path.

Verify Airflow is Running:

```bash
netstat -tulpn | grep 8080
```
If successful, open:
```commandline
http://localhost:8080
```
Administrator Credentials:
The default username is: ```admin```

A random password is generated automatically during the first startup.
cat $AIRFLOW_HOME/simple_auth_manager_passwords.json.generated

# 6. Configure Kaggle credentials

1. Sign in to Kaggle.
2. Open account settings.
3. Create a legacy API key.
4. Download `kaggle.json`.

Install it locally:

```bash
mkdir -p ~/.kaggle
cp ~/Downloads/kaggle.json ~/.kaggle/kaggle.json
chmod 600 ~/.kaggle/kaggle.json
```

Test from virtual env:

```bash
kaggle datasets list -s titanic
kaggle datasets files yasserh/titanic-dataset
```

Never commit `kaggle.json`.

# 7. Configure PostgreSQL

Open PostgreSQL:

```bash
sudo -u postgres psql
```

Run:

```sql
CREATE USER airflow_user WITH PASSWORD '<pwd of your choice>';

CREATE DATABASE airflow_pipeline
    OWNER airflow_user;

GRANT ALL PRIVILEGES
    ON DATABASE airflow_pipeline
    TO airflow_user;
```

Exit:

```sql
\q
```

Test:

```bash
psql -h localhost -p 5432 -U airflow_user -d airflow_pipeline
```

## Create the Airflow connection

The DAG uses connection ID:

```text
pipeline_postgres
```

Create it:

```bash
airflow connections delete pipeline_postgres 2>/dev/null || true

airflow connections add pipeline_postgres \
  --conn-type postgres \
  --conn-host localhost \
  --conn-port 5432 \
  --conn-login airflow_user \
  --conn-password airflow_password \
  --conn-schema airflow_pipeline
```

Verify:

```bash
airflow connections get pipeline_postgres
```

Alternative environment variable:

```bash
export AIRFLOW_CONN_PIPELINE_POSTGRES='postgresql://airflow_user:<passwd>@localhost:5432/airflow_pipeline'
```

# 8. Environment configuration

Create `.env.example`:

```dotenv
PROJECT_ROOT=/absolute/path/to/airflow-data-pipeline-demo
KAGGLE_DATASET_SLUG=yasserh/titanic-dataset
SOURCE_CSV_NAME=Titanic-Dataset.csv
POSTGRES_CONN_ID=pipeline_postgres
DOWNLOAD_DIR=data/downloads
RAW_DIR=data/raw
PROCESSED_DIR=data/processed
SUMMARY_DIR=data/summary
```

Create the local file:

```bash
cp .env.example .env
pwd
nano .env
```

Set `PROJECT_ROOT` to the absolute repository path.

# 9. Start Airflow

For the easiest local setup:

```bash
airflow standalone
```

This initializes the Airflow metadata database and starts the local services. The terminal displays the administrator credentials.

Open:

```text
http://localhost:8080
```

## Separate service mode

```bash
airflow db migrate
```

Then use separate terminals.

Scheduler:

```bash
airflow scheduler
```

API server/UI:

```bash
airflow api-server --port 8080
```

DAG processor:

```bash
airflow dag-processor
```

For a first run, prefer `airflow standalone`.

# 10. Validate the DAG

```bash
airflow dags list
airflow dags list-import-errors
python dags/airflow_pipeline_dag.py
```

Expected DAG ID:

```text
kaggle_postgres_etl
```

Test one task:

```bash
airflow tasks test kaggle_postgres_etl transform_dataset 2026-07-30
```

# 11. Run the pipeline

## Airflow UI

1. Open `http://localhost:8080`.
2. Sign in.
3. Find `kaggle_postgres_etl`.
4. Enable it if required.
5. Select **Trigger DAG**.
6. Open Graph view.
7. Monitor each task.

## CLI

```bash
airflow dags trigger kaggle_postgres_etl
airflow dags list-runs --dag-id kaggle_postgres_etl
```

# 12. Verify PostgreSQL results

```bash
psql -h localhost -U <dbuser> -d <dbname>
```

```sql
\dn
\dt pipeline.*
```

Passenger count:

```sql
SELECT COUNT(*)
FROM pipeline.titanic_passengers;
```

Summary:

```sql
SELECT
    run_id,
    total_rows,
    missing_values,
    survived_count,
    ROUND(survival_rate * 100, 2) AS survival_percentage,
    ROUND(average_age, 2) AS average_age,
    ROUND(average_fare, 2) AS average_fare,
    loaded_at
FROM pipeline.dataset_summary
ORDER BY loaded_at DESC;
```

Audit:

```sql
SELECT
    run_id,
    dag_id,
    task_name,
    status,
    rows_processed,
    recorded_at
FROM pipeline.etl_audit
ORDER BY recorded_at DESC;
```

Example analysis:

```sql
SELECT
    passenger_class,
    COUNT(*) AS passengers,
    ROUND(AVG(survived) * 100, 2) AS survival_percentage
FROM pipeline.titanic_passengers
GROUP BY passenger_class
ORDER BY passenger_class;
```

# 13. Run scripts manually

```bash
python -m scripts.download_dataset
python -m scripts.extract_dataset
python -m scripts.transform_dataset
python -m scripts.generate_summary
python -m scripts.create_tables
python -m scripts.load_postgres
python -m scripts.verify_load
```

# 14. .gitignore

Mentions which files and folders should not be tracked or uploaded to GitHub.

```gitignore
__pycache__/
*.py[cod]
*.egg-info/
.pytest_cache/

airflow-env/
.venv/
venv/

.env
*.env.local
kaggle.json

airflow.cfg
airflow.db
airflow-webserver.pid
standalone_admin_password.txt
logs/
*.log

data/downloads/*
data/raw/*
data/processed/*
data/summary/*

!data/downloads/.gitkeep
!data/raw/.gitkeep
!data/processed/.gitkeep
!data/summary/.gitkeep

.vscode/
.idea/
.DS_Store
```

Create placeholders:

```bash
touch data/downloads/.gitkeep
touch data/raw/.gitkeep
touch data/processed/.gitkeep
touch data/summary/.gitkeep
```

# 15. Pipeline outputs

| Task | Input | Work | Output |
|---|---|---|---|
| `download_dataset` | Kaggle slug | Downloads dataset ZIP | `data/downloads/*.zip` |
| `extract_dataset` | ZIP | Extracts CSV | `data/raw/Titanic-Dataset.csv` |
| `transform_dataset` | Raw CSV | Cleans and engineers fields | Processed CSV |
| `generate_summary` | Processed CSV | Calculates metrics | Summary JSON |
| `create_tables` | SQL script | Creates schema, tables and indexes | PostgreSQL objects |
| `load_postgres` | CSV and JSON | Loads passenger, summary and audit data | PostgreSQL rows |
| `verify_load` | Files and DB | Compares counts and metrics | Success or task failure |

# 16. Data lineage

```text
Kaggle
  └── ZIP
      └── raw CSV
          ├── processed CSV
          │   └── pipeline.titanic_passengers
          └── summary JSON
              └── pipeline.dataset_summary

Airflow run context
  └── pipeline.etl_audit
```

# 17. Future enhancements

- Add Pandera or Great Expectations validation.
- Store raw and processed files in Amazon S3.
- Replace local PostgreSQL with Amazon RDS.
- Add incremental loading instead of truncation.
- Add dataset checksum and version tracking.
- Add failure audit callbacks.
- Add Slack or email notifications.
- Add Docker Compose.
- Add GitHub Actions for tests and DAG validation.
- Add dbt transformations.
- Add Apache Superset or Power BI reporting.
- Parameterize the dataset with Airflow Variables.

# 18. Useful commands

```bash
source airflow-env/bin/activate
airflow version
airflow standalone
airflow dags list
airflow dags list-import-errors
airflow dags trigger kaggle_postgres_etl
airflow dags list-runs --dag-id kaggle_postgres_etl
airflow connections get pipeline_postgres
python -m pytest -v
psql -h localhost -U <dbuser> -d <dbname>
```

# Learning outcome

After completing this project, a developer should be able to explain:

1. How Airflow models workflows as DAGs.
2. How task dependencies determine execution order.
3. How raw and processed data are separated.
4. How summary and audit records are generated.
5. How Airflow connects to PostgreSQL.
6. How SQL scripts create version-controlled database objects.
7. How transformed records are loaded into relational tables.
8. How verification tasks fail a DAG when expectations are not met.

## License

This project is intended for learning, demonstration, and portfolio use.