"""
Clean a synthetic gym membership export and prepare it for BI consumption.

Example:
    python clean_membership_data.py \
        --input data/raw/membership_export.csv \
        --output data/processed/membership_export_clean.csv \
        --reference-date 2026-01-31

This script is intended for portfolio demonstration only.
It does not use or reference any real customer or company data.
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = {
    "member_id",
    "full_name",
    "email",
    "signup_date",
    "last_checkin_date",
    "membership_status",
    "plan_name",
    "monthly_fee",
    "partner_name",
}

TEXT_COLUMNS = ["full_name", "email", "membership_status", "plan_name", "partner_name"]
DATE_COLUMNS = ["signup_date", "last_checkin_date"]
NUMERIC_COLUMNS = ["monthly_fee"]

PLAN_NAME_MAPPING = {
    "basic": "Basic",
    "basic plan": "Basic",
    "premium": "Premium",
    "premium plus": "Premium Plus",
    "corporate": "Corporate",
}


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Clean a synthetic membership export for analysis and BI consumption.",
    )
    parser.add_argument("--input", required=True, type=Path, help="Path to the raw CSV file.")
    parser.add_argument("--output", required=True, type=Path, help="Path to the cleaned CSV file.")
    parser.add_argument(
        "--reference-date",
        type=str,
        default=None,
        help="Optional YYYY-MM-DD date used to calculate recency flags.",
    )
    return parser.parse_args()


def load_dataset(input_path: Path) -> pd.DataFrame:
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    logging.info("Loading dataset from %s", input_path)
    return pd.read_csv(input_path)


def standardize_column_names(dataframe: pd.DataFrame) -> pd.DataFrame:
    cleaned_dataframe = dataframe.copy()
    cleaned_dataframe.columns = (
        cleaned_dataframe.columns.str.strip()
        .str.lower()
        .str.replace(r"[^a-z0-9]+", "_", regex=True)
        .str.strip("_")
    )
    return cleaned_dataframe


def validate_required_columns(dataframe: pd.DataFrame) -> None:
    missing_columns = REQUIRED_COLUMNS.difference(dataframe.columns)
    if missing_columns:
        missing_list = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required columns: {missing_list}")


def clean_text_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    cleaned_dataframe = dataframe.copy()

    for column_name in TEXT_COLUMNS:
        cleaned_dataframe[column_name] = cleaned_dataframe[column_name].astype("string").str.strip()

    cleaned_dataframe["full_name"] = cleaned_dataframe["full_name"].str.title()
    cleaned_dataframe["email"] = cleaned_dataframe["email"].str.lower()
    cleaned_dataframe["membership_status"] = cleaned_dataframe["membership_status"].str.lower()
    cleaned_dataframe["partner_name"] = cleaned_dataframe["partner_name"].str.title()

    return cleaned_dataframe


def parse_date_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    parsed_dataframe = dataframe.copy()

    for column_name in DATE_COLUMNS:
        parsed_dataframe[column_name] = pd.to_datetime(
            parsed_dataframe[column_name],
            errors="coerce",
        )

    return parsed_dataframe


def clean_numeric_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    cleaned_dataframe = dataframe.copy()

    for column_name in NUMERIC_COLUMNS:
        cleaned_dataframe[column_name] = pd.to_numeric(
            cleaned_dataframe[column_name],
            errors="coerce",
        )

    return cleaned_dataframe


def normalize_plan_names(dataframe: pd.DataFrame) -> pd.DataFrame:
    normalized_dataframe = dataframe.copy()
    normalized_plan_names = normalized_dataframe["plan_name"].str.lower().map(PLAN_NAME_MAPPING)
    normalized_dataframe["plan_name"] = normalized_plan_names.fillna(
        normalized_dataframe["plan_name"].str.title()
    )
    return normalized_dataframe


def remove_invalid_rows(dataframe: pd.DataFrame) -> pd.DataFrame:
    filtered_dataframe = dataframe.copy()

    filtered_dataframe = filtered_dataframe.dropna(
        subset=["member_id", "email", "signup_date", "membership_status", "plan_name"]
    )
    filtered_dataframe = filtered_dataframe[filtered_dataframe["monthly_fee"].fillna(0) >= 0]
    filtered_dataframe = filtered_dataframe[
        filtered_dataframe["membership_status"].isin({"active", "paused", "cancelled"})
    ]
    filtered_dataframe = filtered_dataframe.drop_duplicates(subset=["member_id"], keep="last")

    return filtered_dataframe


def add_business_flags(dataframe: pd.DataFrame, reference_date: pd.Timestamp) -> pd.DataFrame:
    enriched_dataframe = dataframe.copy()
    normalized_reference_date = reference_date.normalize()

    enriched_dataframe["days_since_last_checkin"] = (
        normalized_reference_date - enriched_dataframe["last_checkin_date"]
    ).dt.days
    enriched_dataframe["days_since_signup"] = (
        normalized_reference_date - enriched_dataframe["signup_date"]
    ).dt.days

    enriched_dataframe["member_health_flag"] = "healthy"
    enriched_dataframe.loc[
        enriched_dataframe["days_since_last_checkin"].fillna(999) > 30,
        "member_health_flag",
    ] = "at_risk"
    enriched_dataframe.loc[
        enriched_dataframe["days_since_last_checkin"].fillna(999) > 60,
        "member_health_flag",
    ] = "inactive"

    enriched_dataframe["is_currently_active"] = (
        enriched_dataframe["membership_status"] == "active"
    )

    return enriched_dataframe


def sort_dataset(dataframe: pd.DataFrame) -> pd.DataFrame:
    return dataframe.sort_values(
        by=["partner_name", "plan_name", "full_name"],
        ascending=[True, True, True],
    ).reset_index(drop=True)


def export_dataset(dataframe: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(output_path, index=False)
    logging.info("Clean dataset exported to %s", output_path)


def clean_membership_dataset(
    dataframe: pd.DataFrame,
    reference_date: pd.Timestamp,
) -> pd.DataFrame:
    standardized_dataframe = standardize_column_names(dataframe)
    validate_required_columns(standardized_dataframe)

    cleaned_dataframe = clean_text_columns(standardized_dataframe)
    cleaned_dataframe = parse_date_columns(cleaned_dataframe)
    cleaned_dataframe = clean_numeric_columns(cleaned_dataframe)
    cleaned_dataframe = normalize_plan_names(cleaned_dataframe)
    cleaned_dataframe = remove_invalid_rows(cleaned_dataframe)
    cleaned_dataframe = add_business_flags(cleaned_dataframe, reference_date)

    return sort_dataset(cleaned_dataframe)


def main() -> None:
    configure_logging()
    arguments = parse_arguments()

    reference_date = (
        pd.Timestamp(arguments.reference_date)
        if arguments.reference_date
        else pd.Timestamp.utcnow().normalize()
    )

    raw_dataset = load_dataset(arguments.input)
    cleaned_dataset = clean_membership_dataset(raw_dataset, reference_date)
    export_dataset(cleaned_dataset, arguments.output)


if __name__ == "__main__":
    main()

