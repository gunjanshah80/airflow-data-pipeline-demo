from __future__ import annotations

import json

import pandas as pd

from scripts import common, generate_summary, transform_data


def test_create_directories_creates_expected_folders(tmp_path, monkeypatch):
    base_dir = tmp_path / "project"

    monkeypatch.setattr(common, "DOWNLOAD_DIR", base_dir / "data" / "downloads")
    monkeypatch.setattr(common, "RAW_DIR", base_dir / "data" / "raw")
    monkeypatch.setattr(common, "PROCESSED_DIR", base_dir / "data" / "processed")
    monkeypatch.setattr(common, "SUMMARY_DIR", base_dir / "data" / "summary")

    common.create_directories()

    for directory in (
        base_dir / "data" / "downloads",
        base_dir / "data" / "raw",
        base_dir / "data" / "processed",
        base_dir / "data" / "summary",
    ):
        assert directory.is_dir()


def test_transform_dataset_creates_processed_csv(tmp_path, monkeypatch):
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    raw_dir.mkdir()
    processed_dir.mkdir()

    raw_file = raw_dir / "Titanic-Dataset.csv"
    processed_file = processed_dir / "titanic_processed.csv"

    frame = pd.DataFrame(
        {
            "PassengerId": [1, 1, 2],
            "Survived": [0, 0, 1],
            "Pclass": [1, 1, 3],
            "Name": ["Alice", "Alice", "Bob"],
            "Sex": ["female", "female", "male"],
            "Age": [None, 28.0, 35.0],
            "SibSp": [0, 1, 0],
            "Parch": [0, 0, 2],
            "Ticket": ["A", "B", "C"],
            "Fare": [10.5, None, 15.0],
            "Cabin": [None, "C65", None],
            "Embarked": ["S", None, "C"],
        }
    )
    frame.to_csv(raw_file, index=False)

    monkeypatch.setattr(transform_data, "RAW_CSV_PATH", raw_file)
    monkeypatch.setattr(transform_data, "PROCESSED_CSV_PATH", processed_file)

    result_path = transform_data.transform_dataset()

    assert result_path == str(processed_file)
    assert processed_file.exists()

    transformed = pd.read_csv(processed_file)
    assert "passenger_id" in transformed.columns
    assert "passenger_class" in transformed.columns
    assert "family_size" in transformed.columns
    assert "age_group" in transformed.columns
    assert len(transformed) == 2
    assert transformed["age"].notna().all()
    assert transformed["fare"].notna().all()


def test_generate_summary_writes_expected_json(tmp_path, monkeypatch):
    processed_file = tmp_path / "titanic_processed.csv"
    summary_file = tmp_path / "dataset_summary.json"

    pd.DataFrame(
        {
            "passenger_id": [1, 2, 3],
            "survived": [0, 1, 1],
            "age": [25.0, 30.0, 35.0],
            "fare": [10.0, 20.0, 30.0],
            "passenger_class": [1, 2, 3],
        }
    ).to_csv(processed_file, index=False)

    monkeypatch.setattr(generate_summary, "PROCESSED_CSV_PATH", processed_file)
    monkeypatch.setattr(generate_summary, "SUMMARY_JSON_PATH", summary_file)

    result_path = generate_summary.generate_summary()

    assert result_path == str(summary_file)
    assert summary_file.exists()

    payload = json.loads(summary_file.read_text(encoding="utf-8"))
    assert payload["total_rows"] == 3
    assert payload["total_columns"] == 5
    assert payload["survived_count"] == 2
    assert "generated_at_utc" in payload
