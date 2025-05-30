# tests/test_data_loader.py

import os
import pandas as pd
import tempfile

from utils.data_loader import load_body_measurements, load_shirt_data

# --- Fixtures: create temp sample CSVs ---

def write_temp_csv(content: str):
    """Helper to write CSV content to a temp file, return file path."""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode='w', encoding='utf-8')
    tmp.write(content)
    tmp.close()
    return tmp.name

def test_load_body_measurements_standard():
    csv = """Measurement,Value
ChestWidth,18.5
ShoulderWidth,17.0
TorsoLength,27.0
HemWidth,18.0
SleeveLength,8.0
"""
    path = write_temp_csv(csv)
    body = load_body_measurements(path)
    assert isinstance(body, dict)
    assert set(body) == {'ChestWidth', 'ShoulderWidth', 'TorsoLength', 'HemWidth', 'SleeveLength'}
    assert abs(body['ChestWidth'] - 18.5) < 1e-6
    os.unlink(path)

def test_load_body_measurements_keyval():
    csv = """ChestWidth,ShoulderWidth,TorsoLength,HemWidth,SleeveLength
18.5,17.0,27.0,18.0,8.0
"""
    path = write_temp_csv(csv)
    body = load_body_measurements(path)
    assert isinstance(body, dict)
    assert body['HemWidth'] == 18.0
    assert body['SleeveLength'] == 8.0
    os.unlink(path)

def test_load_shirt_data_basic():
    csv = """ShirtName,ChestWidth,ShoulderWidth,BodyLength,HemWidth,SleeveLength,Weight
Test Tee,19.0,17.0,27.5,18.0,8.5,5.5
"""
    path = write_temp_csv(csv)
    df = load_shirt_data(path)
    assert isinstance(df, pd.DataFrame)
    assert "Weight" in df.columns
    assert abs(df.iloc[0]["Weight"] - 5.5) < 1e-6
    os.unlink(path)

def test_load_shirt_data_weight_oz_col():
    csv = """ShirtName,WeightOz
Test Tee,6.3
"""
    path = write_temp_csv(csv)
    df = load_shirt_data(path)
    assert "Weight" in df.columns
    assert abs(df.iloc[0]["Weight"] - 6.3) < 1e-6
    os.unlink(path)

def test_load_shirt_data_weight_lowercase_col():
    csv = """ShirtName,weight
Test Tee,6.7
"""
    path = write_temp_csv(csv)
    df = load_shirt_data(path)
    assert "Weight" in df.columns
    assert abs(df.iloc[0]["Weight"] - 6.7) < 1e-6
    os.unlink(path)

def test_load_shirt_data_trims_columns():
    csv = """  ShirtName  ,  ChestWidth  , WeightOz
Test Tee,19.0,5.5
"""
    path = write_temp_csv(csv)
    df = load_shirt_data(path)
    assert "ShirtName" in df.columns
    assert "ChestWidth" in df.columns
    assert abs(df.iloc[0]["Weight"] - 5.5) < 1e-6
    os.unlink(path)

# --- Bonus: check error handling for missing columns ---

def test_load_body_measurements_missing_cols():
    csv = "Nope,Nothing\nfoo,bar\n"
    path = write_temp_csv(csv)
    body = load_body_measurements(path)
    assert isinstance(body, dict)  # Should not error, just returns whatever mapping
    os.unlink(path)
