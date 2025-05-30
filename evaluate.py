# evaluate.py
# Evaluates t-shirt fit for each garment using the refined `score_fit` model.

import os
import pandas as pd
from tabulate import tabulate
from utils.data_loader import load_body_measurements, load_shirt_data
from models.fit_model import score_fit, bulk_projection_profile

import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


def score_shirts(body, shirts):
    """
    Scores each shirt for both current and bulk profiles.
    Returns a list of dicts, one per shirt.
    """
    bulk_profile = bulk_projection_profile(body)
    results = []
    for idx, row in shirts.iterrows():
        shirt = row.to_dict()
        # Normal fit
        normal = score_fit(body, shirt)
        # Bulk fit
        bulk = score_fit(bulk_profile, shirt)
        results.append(
            {
                "ShirtName": shirt.get("ShirtName", f"Shirt_{idx}"),
                "FitScore": normal["FitScore"],
                "Confidence": normal["Confidence"],
                "Tags": "; ".join(normal.get("Tags", [])),
                "Rationale": normal.get("Rationale", ""),
                "BulkFitScore": bulk["FitScore"],
                "BulkConfidence": int(round(bulk["Confidence"] * 0.85)),  # Lowered for projection
                "BulkTags": "; ".join(bulk.get("Tags", [])),
                "BulkRationale": bulk.get("Rationale", ""),
            }
        )
    return results


def evaluate_fit(body_path, shirt_path, out_path):
    body = load_body_measurements(body_path)
    shirts = load_shirt_data(shirt_path)
    results = score_shirts(body, shirts)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    df = pd.DataFrame(results)
    df.to_csv(out_path, index=False)
    return results  # For testing or inspection


def main():
    # Show full strings in pandas output (no truncation)
    pd.set_option("display.max_colwidth", None)
    BODY_PATH = "data/body_measurements.csv"
    SHIRT_PATH = "data/shirt_data.csv"

    OUT_PATH = "outputs/fit_results.csv"

    # Verify input files exist
    if not os.path.exists(BODY_PATH) or not os.path.exists(SHIRT_PATH):
        print(
            "Missing input data. Please check data/body_measurements.csv and data/shirt_data.csv."
        )
        return

    # Load body measurements (returns dict) and shirt data (returns DataFrame)
    results = evaluate_fit(body_path, shirt_path, out_path)

    # Print a brief summary (prettified)
    display_cols = [
        ("ShirtName", "Shirt name"),
        ("FitScore", "Score"),
        ("Confidence", "Conf."),
        ("BulkFitScore", "Bulk score"),
        ("BulkConfidence", "Bulk conf."),
    ]

    # Subset and rename columns for display
    display_df = df[[c[0] for c in display_cols]].copy()
    display_df.columns = [c[1] for c in display_cols]

    # Format numeric columns to two decimals if present
    for col in ["Score", "Conf.", "Bulk score", "Bulk conf."]:
        display_df[col] = display_df[col].apply(
            lambda x: f"{float(x):.2f}" if x not in ["", None, "nan"] and str(x) != "" else ""
        )

    print("\nFitting Results:\n")
    print(tabulate(display_df, headers="keys", tablefmt="fancy_grid", showindex=False))


if __name__ == "__main__":
    main()
