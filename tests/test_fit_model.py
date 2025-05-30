import os
import pytest
from utils.data_loader import load_body_measurements, load_shirt_data
from models.fit_model import score_fit, bulk_projection_profile

DATA_DIR = os.path.dirname(__file__)

def test_score_fit_on_sample_data():
    body = load_body_measurements(os.path.join(DATA_DIR, 'sample_body.csv'))
    shirts = load_shirt_data(os.path.join(DATA_DIR, 'sample_shirts.csv'))
    row = shirts.iloc[0].to_dict()
    result = score_fit(body, row)
    assert isinstance(result['FitScore'], (int, float)), "FitScore should be numeric"
    assert 0 <= result['FitScore'] <= 100, "FitScore out of range"
    assert isinstance(result['Confidence'], int)
    assert 0 <= result['Confidence'] <= 100, "Confidence out of range"

def test_score_fit_boxy_shirt_higher():
    body = load_body_measurements(os.path.join(DATA_DIR, 'sample_body.csv'))
    shirts = load_shirt_data(os.path.join(DATA_DIR, 'sample_shirts.csv'))
    boxy_score = score_fit(body, shirts.iloc[1].to_dict())['FitScore']
    tight_score = score_fit(body, shirts.iloc[2].to_dict())['FitScore']
    assert boxy_score > tight_score, "Boxy/oversize shirt should rate higher than tight shirt"

def test_comically_oversized_penalized():
    body = {"ChestWidth": 19, "ShoulderWidth": 17, "TorsoLength": 15}
    # Huge, very lightweight shirt
    shirt = {"ChestWidth": 29, "ShoulderWidth": 25, "TorsoLength": 22, "Weight": 3.8}
    result = score_fit(body, shirt)
    assert "Comically Oversized" in result.get("Tags", []), "Should tag as Comically Oversized"
    assert result["FitScore"] < 65, "Comically oversized lightweight shirt should score low"

def test_bulk_projection_increases_bulk_fields():
    body = load_body_measurements(os.path.join(DATA_DIR, 'sample_body.csv'))
    bulk = bulk_projection_profile(body)
    # Only test fields present in both
    for key in ['ChestWidth', 'ShoulderWidth']:
        if key in body and key in bulk:
            assert bulk[key] > body[key], f"{key} should increase for bulk profile"
    if 'TorsoLength' in body:
        assert bulk['TorsoLength'] == body['TorsoLength'], "TorsoLength should stay the same unless modeling a growth spurt"

def test_score_fit_with_missing_fields():
    body = {"ChestWidth": 18.5}
    shirt = {"Weight": 4.5}
    result = score_fit(body, shirt)
    assert isinstance(result['FitScore'], (int, float)), "Should still return numeric FitScore with partial data"
    assert result['Confidence'] < 100, "Confidence should be reduced when data is missing"

def test_score_fit_extremes():
    # Unrealistically small and large shirts
    body = {"ChestWidth": 19, "ShoulderWidth": 17, "TorsoLength": 15}
    tiny = {"ChestWidth": 15, "ShoulderWidth": 14, "TorsoLength": 12, "Weight": 3.5}
    huge = {"ChestWidth": 25, "ShoulderWidth": 23, "TorsoLength": 22, "Weight": 8}
    tiny_score = score_fit(body, tiny)['FitScore']
    huge_score = score_fit(body, huge)['FitScore']
    assert tiny_score < 60, "Tiny shirt should score very low"
    assert huge_score > tiny_score, "Huge shirt should outscore tiny shirt for a relaxed fit lover"
    # Optionally, ensure it's not absurdly high either:
    assert huge_score < 85, "Huge shirt should not be an ideal fit"

def test_tags_and_rationale_present():
    body = load_body_measurements(os.path.join(DATA_DIR, 'sample_body.csv'))
    shirts = load_shirt_data(os.path.join(DATA_DIR, 'sample_shirts.csv'))
    row = shirts.iloc[0].to_dict()
    result = score_fit(body, row)
    assert 'Tags' in result and isinstance(result['Tags'], list), "Tags should be a list"
    assert 'Rationale' in result and isinstance(result['Rationale'], str), "Rationale should be a string"

def test_bulk_confidence_lower():
    body = load_body_measurements(os.path.join(DATA_DIR, 'sample_body.csv'))
    shirts = load_shirt_data(os.path.join(DATA_DIR, 'sample_shirts.csv'))
    shirt = shirts.iloc[0].to_dict()
    normal = score_fit(body, shirt)
    bulk = score_fit(bulk_projection_profile(body), shirt)
    assert bulk['Confidence'] <= normal['Confidence'], "Bulk confidence should not exceed normal profile confidence"
