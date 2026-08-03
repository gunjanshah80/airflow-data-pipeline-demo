from __future__ import annotations

import pandas as pd

from scripts.common import PROCESSED_CSV_PATH, RAW_CSV_PATH, create_directories

REQUIRED_COLUMNS = {
    "PassengerId", "Survived", "Pclass", "Name", "Sex", "Age",
    "SibSp", "Parch", "Ticket", "Fare", "Cabin", "Embarked",
}

def transform_dataset() -> str:

    if not RAW_CSV_PATH.exists():
        raise FileNotFoundError(f"Raw file not found: {RAW_CSV_PATH}")

    dataframe = pd.read_csv(RAW_CSV_PATH)
    missing_columns = REQUIRED_COLUMNS.difference(dataframe.columns)

    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

    dataframe = dataframe.drop_duplicates(subset=["PassengerId"]).copy()
    dataframe["Age"] = dataframe["Age"].fillna(dataframe["Age"].median())
    dataframe["Fare"] = dataframe["Fare"].fillna(dataframe["Fare"].median())

    mode_embarked = dataframe["Embarked"].mode()
    dataframe["Embarked"] = dataframe["Embarked"].fillna(
        mode_embarked.iloc[0] if not mode_embarked.empty else "Unknown"
    )
    dataframe["Cabin"] = dataframe["Cabin"].fillna("Unknown")
    dataframe["FamilySize"] = dataframe["SibSp"] + dataframe["Parch"] + 1
    dataframe["IsAlone"] = (dataframe["FamilySize"] == 1).astype(int)
    dataframe["AgeGroup"] = pd.cut(
        dataframe["Age"],
        bins=[0, 12, 18, 35, 60, float("inf")],
        labels=["Child", "Teenager", "Young Adult", "Adult", "Senior"],
        include_lowest=True,
    ).astype(str)

    dataframe.columns = [column.strip().lower() for column in dataframe.columns]
    dataframe = dataframe.rename(columns={
        "passengerid": "passenger_id",
        "pclass": "passenger_class",
        "sibsp": "siblings_spouses",
        "parch": "parents_children",
        "familysize": "family_size",
        "isalone": "is_alone",
        "agegroup": "age_group",
    })

    dataframe.to_csv(PROCESSED_CSV_PATH, index=False)
    print(f"Saved {len(dataframe)} rows to {PROCESSED_CSV_PATH}")
    return str(PROCESSED_CSV_PATH)


if __name__ == "__main__":
    transform_dataset()