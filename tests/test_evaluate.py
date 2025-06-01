# tests/test_evaluate.py

import os
import pandas as pd
import pytest
from utils.data_loader import load_body_measurements, load_shirt_data
from evaluate import score_shirts, evaluate_fit

# Paths to test data (relative to this test file)
BODY_PATH = os.path.join(os.path.dirname(__file__), "sample_body.csv")
SHIRT_PATH = os.path.join(os.path.dirname(__file__), "sample_shirts.csv")

def test_score_shirts_with_sample_data():
    body = load_body_measurements(BODY_PATH)
    shirts = load_shirt_data(SHIRT_PATH)
    results = score_shirts(body, shirts)
    assert isinstance(results, list)
    assert all("FitScore" in r for r in results)
    assert all("BulkFitScore" in r for r in results)
    assert len(results) == 3  # Three shirts in the sample file
    # Sanity check values
    for res in results:
        assert 0 <= res["FitScore"] <= 100 or res["FitScore"] == ""  # "" for missing data
        assert 0 <= res["BulkFitScore"] <= 100 or res["BulkFitScore"] == ""
        assert isinstance(res["ShirtName"], str)


def test_evaluate_fit_pipeline(tmp_path):
    # Use the sample files, but output to a temp dir so nothing is overwritten
    out_path = tmp_path / "fit_results.csv"
    results = evaluate_fit(body_path=BODY_PATH, shirt_path=SHIRT_PATH, out_path=str(out_path))
    assert os.path.exists(out_path)
    df = pd.read_csv(out_path)
    assert not df.empty
    # Check that the main columns are present
    for col in ["ShirtName", "FitScore", "BulkFitScore"]:
        assert col in df.columns


def test_score_shirts_with_style_profile():
    body = load_body_measurements(BODY_PATH)
    shirts = load_shirt_data(SHIRT_PATH)
    # Use a style profile that exists (e.g., 'relaxed'), adjust as needed
    results = score_shirts(body, shirts, style_profile="relaxed")
    assert isinstance(results, list)
    # Each result must include StyleFitScore and StyleProfile
    assert all("StyleFitScore" in r for r in results)
    assert all(r.get("StyleProfile") == "relaxed" for r in results)
    # Ensure core FitScore still present
    assert all("FitScore" in r for r in results)
        # StyleFitScore should be numeric. We don’t assume difference.
    for r in results:
        assert isinstance(r.get("StyleFitScore"), (int, float))
    # Ensure not all style scores equal core scores
    all_equal = all(r.get("StyleFitScore") == r.get("FitScore") for r in results)
    assert not all_equal, "All StyleFitScore values are identical to FitScore; overlay not applied."


@pytest.mark.parametrize("profile", ["relaxed", "slim"])
def test_evaluate_fit_with_style_writes_correct_columns(tmp_path, profile):
    out_path = tmp_path / "fit_results_style.csv"
    # Generate output with a given style profile
    results = evaluate_fit(body_path=BODY_PATH, shirt_path=SHIRT_PATH, out_path=str(out_path), style_profile=profile)
    assert os.path.exists(out_path)
    df = pd.read_csv(out_path)
    # The CSV must include StyleFitScore and StyleProfile columns
    for col in ["ShirtName", "StyleFitScore", "StyleProfile"]:
        assert col in df.columns
    # Check that all rows have the correct StyleProfile
    assert all(df["StyleProfile"] == profile)
