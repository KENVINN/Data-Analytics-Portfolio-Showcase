"""
Clean a synthetic Maker Info service order export and prepare it for BI consumption.

Example:
    python clean_service_orders_data.py \
        --input Synthetic_Data/service_orders_raw.csv \
        --output Synthetic_Data/service_orders_clean.csv \
        --reference-date 2026-04-15

This script is intended for portfolio demonstration only.
It does not use or reference any real customer or company data.
"""

from __future__ import annotations

import argparse
import logging
import re
from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = {
    "order_id",
    "customer_name",
    "phone_number",
    "company_name",
    "service_line",
    "device_type",
    "current_status",
    "opened_at",
    "closed_at",
    "quoted_amount_brl",
    "approved_revenue_brl",
    "technician_name",
    "city",
    "sla_target_hours",
}

TEXT_COLUMNS = [
    "customer_name",
    "phone_number",
    "company_name",
    "service_line",
    "device_type",
    "current_status",
    "technician_name",
    "city",
]

DATETIME_COLUMNS = ["opened_at", "closed_at"]
NUMERIC_COLUMNS = ["quoted_amount_brl", "approved_revenue_brl", "sla_target_hours"]

SERVICE_LINE_MAPPING = {
    "computer repair": "Computer Repair",
    "mobile repair": "Mobile Repair",
    "b2b support": "B2B Support",
    "onsite visit": "Onsite Visit",
}

STATUS_MAPPING = {
    "delivered": "delivered",
    "ready for pickup": "ready_for_pickup",
    "ready for pick up": "ready_for_pickup",
    "in repair": "in_repair",
    "awaiting part": "awaiting_part",
    "quote rejected": "quote_rejected",
    "cancelled": "cancelled",
}


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Clean a synthetic service order export for analysis and BI consumption.",
    )
    parser.add_argument("--input", required=True, type=Path, help="Path to the raw CSV file.")
    parser.add_argument("--output", required=True, type=Path, help="Path to the cleaned CSV file.")
    parser.add_argument(
        "--reference-date",
        type=str,
        default=None,
        help="Optional YYYY-MM-DD date used to calculate aging and SLA risk flags.",
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


def normalize_lookup_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def validate_required_columns(dataframe: pd.DataFrame) -> None:
    missing_columns = REQUIRED_COLUMNS.difference(dataframe.columns)
    if missing_columns:
        missing_list = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required columns: {missing_list}")


def clean_text_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    cleaned_dataframe = dataframe.copy()

    for column_name in TEXT_COLUMNS:
        cleaned_dataframe[column_name] = cleaned_dataframe[column_name].astype("string").str.strip()

    cleaned_dataframe["customer_name"] = cleaned_dataframe["customer_name"].str.title()
    cleaned_dataframe["company_name"] = cleaned_dataframe["company_name"].str.title()
    cleaned_dataframe["device_type"] = cleaned_dataframe["device_type"].str.title()
    cleaned_dataframe["technician_name"] = cleaned_dataframe["technician_name"].str.title()
    cleaned_dataframe["city"] = cleaned_dataframe["city"].str.title()
    cleaned_dataframe["phone_number"] = (
        cleaned_dataframe["phone_number"].str.replace(r"[^0-9]+", "", regex=True)
    )

    cleaned_dataframe["service_line"] = (
        cleaned_dataframe["service_line"]
        .apply(normalize_lookup_key)
        .map(SERVICE_LINE_MAPPING)
        .fillna(cleaned_dataframe["service_line"].str.strip().str.title())
    )

    cleaned_dataframe["current_status"] = (
        cleaned_dataframe["current_status"]
        .apply(normalize_lookup_key)
        .map(STATUS_MAPPING)
        .fillna(cleaned_dataframe["current_status"].apply(normalize_lookup_key).str.replace(" ", "_"))
    )

    return cleaned_dataframe


def parse_datetime_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    parsed_dataframe = dataframe.copy()

    for column_name in DATETIME_COLUMNS:
        parsed_dataframe[column_name] = pd.to_datetime(
            parsed_dataframe[column_name],
            errors="coerce",
        )

    return parsed_dataframe


def clean_numeric_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    cleaned_dataframe = dataframe.copy()

    for column_name in NUMERIC_COLUMNS:
        normalized_series = (
            cleaned_dataframe[column_name]
            .astype("string")
            .str.replace(r"[^0-9.\-]+", "", regex=True)
            .replace({"": pd.NA, ".": pd.NA, "-": pd.NA})
        )
        cleaned_dataframe[column_name] = pd.to_numeric(normalized_series, errors="coerce")

    return cleaned_dataframe


def remove_invalid_rows(dataframe: pd.DataFrame) -> pd.DataFrame:
    filtered_dataframe = dataframe.copy()

    filtered_dataframe = filtered_dataframe.dropna(
        subset=["order_id", "customer_name", "current_status", "opened_at", "company_name"]
    )
    filtered_dataframe = filtered_dataframe[
        filtered_dataframe["quoted_amount_brl"].fillna(0) >= 0
    ]
    filtered_dataframe = filtered_dataframe[
        filtered_dataframe["approved_revenue_brl"].fillna(0) >= 0
    ]
    filtered_dataframe = filtered_dataframe[
        filtered_dataframe["sla_target_hours"].fillna(0) > 0
    ]
    filtered_dataframe = filtered_dataframe.drop_duplicates(subset=["order_id"], keep="last")

    return filtered_dataframe


def add_business_flags(dataframe: pd.DataFrame, reference_date: pd.Timestamp) -> pd.DataFrame:
    enriched_dataframe = dataframe.copy()
    reference_timestamp = reference_date.normalize() + pd.Timedelta(hours=23, minutes=59)

    resolution_end = enriched_dataframe["closed_at"].fillna(reference_timestamp)
    enriched_dataframe["hours_open"] = (
        (resolution_end - enriched_dataframe["opened_at"]).dt.total_seconds() / 3600
    ).round(2)
    enriched_dataframe["hours_to_close"] = (
        (enriched_dataframe["closed_at"] - enriched_dataframe["opened_at"]).dt.total_seconds() / 3600
    ).round(2)
    enriched_dataframe["revenue_realization_gap_brl"] = (
        enriched_dataframe["quoted_amount_brl"] - enriched_dataframe["approved_revenue_brl"]
    ).round(2)

    enriched_dataframe["is_b2b_account"] = (
        enriched_dataframe["company_name"].str.lower() != "retail direct"
    )

    enriched_dataframe["order_health_flag"] = "on_track"
    enriched_dataframe.loc[
        enriched_dataframe["current_status"].isin({"quote_rejected", "cancelled"}),
        "order_health_flag",
    ] = "lost_revenue"
    enriched_dataframe.loc[
        enriched_dataframe["closed_at"].notna()
        & (enriched_dataframe["hours_to_close"] > enriched_dataframe["sla_target_hours"]),
        "order_health_flag",
    ] = "sla_breached"
    enriched_dataframe.loc[
        enriched_dataframe["closed_at"].isna()
        & (enriched_dataframe["hours_open"] > enriched_dataframe["sla_target_hours"]),
        "order_health_flag",
    ] = "attention_required"
    enriched_dataframe.loc[
        enriched_dataframe["closed_at"].isna()
        & (enriched_dataframe["hours_open"] > enriched_dataframe["sla_target_hours"] * 1.5),
        "order_health_flag",
    ] = "critical_delay"

    return enriched_dataframe


def sort_dataset(dataframe: pd.DataFrame) -> pd.DataFrame:
    return dataframe.sort_values(
        by=["company_name", "current_status", "opened_at"],
        ascending=[True, True, False],
    ).reset_index(drop=True)


def export_dataset(dataframe: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(output_path, index=False)
    logging.info("Clean dataset exported to %s", output_path)


def clean_service_orders_dataset(
    dataframe: pd.DataFrame,
    reference_date: pd.Timestamp,
) -> pd.DataFrame:
    standardized_dataframe = standardize_column_names(dataframe)
    validate_required_columns(standardized_dataframe)

    cleaned_dataframe = clean_text_columns(standardized_dataframe)
    cleaned_dataframe = parse_datetime_columns(cleaned_dataframe)
    cleaned_dataframe = clean_numeric_columns(cleaned_dataframe)
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
    cleaned_dataset = clean_service_orders_dataset(raw_dataset, reference_date)
    export_dataset(cleaned_dataset, arguments.output)


if __name__ == "__main__":
    main()

