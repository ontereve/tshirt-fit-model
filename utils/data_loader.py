# utils/data_loader.py
"""
Utility functions for loading body measurements and shirt data from CSV files.
Handles flexible formats, robust column cleaning, and automatic weight field detection.
"""

import logging
from typing import Dict
import pandas as pd

logger = logging.getLogger(__name__)


def load_body_measurements(path: str) -> Dict[str, float]:
    """
    Loads body measurements from a CSV file.
    Supports two formats:
      1. 'Measurement', 'Value' columns (vertical)
      2. Single-row key-value mapping (horizontal)
    Returns a dictionary mapping measurement names to float values.
    """
    try:
        df = pd.read_csv(path)
        if df.empty:
            logger.warning(f"Body measurements file '{path}' is empty.")
            return {}
        df.columns = [col.strip() for col in df.columns]

        if "Measurement" in df.columns and "Value" in df.columns:
            body = pd.Series(df.Value.values, index=df.Measurement).astype(float).to_dict()
        else:
            # Single-row key-value mapping
            body = df.iloc[0].astype(float).to_dict()
        return body
    except (ValueError, KeyError, FileNotFoundError) as e:
        logger.error(f"Failed to load body measurements from '{path}': {e}")
        return {}


def load_shirt_data(path: str) -> pd.DataFrame:
    """
    Loads shirt data from a CSV file, normalizing weight and column names.
    Adds a 'Weight' column if needed, using 'WeightOz' or 'weight' if present.
    Returns a pandas DataFrame.
    """
    try:
        df = pd.read_csv(path)
        if df.empty:
            logger.warning(f"Shirt data file '{path}' is empty.")
            return pd.DataFrame()
        # Clean column names
        df.columns = [col.strip() for col in df.columns]

        # Normalize 'Weight' column (auto-detect various possible names)
        weight_col = None
        for candidate in ["Weight", "WeightOz", "weight", "weightoz"]:
            if candidate in df.columns:
                weight_col = candidate
                break
        if weight_col and weight_col != "Weight":
            df["Weight"] = df[weight_col].astype(float)
        elif "Weight" in df.columns:
            df["Weight"] = df["Weight"].astype(float)
        else:
            # No weight column, add as NaN for consistency
            df["Weight"] = float("nan")

        return df
    except Exception as e:
        logger.error(f"Failed to load shirt data from '{path}': {e}")
        return pd.DataFrame()
