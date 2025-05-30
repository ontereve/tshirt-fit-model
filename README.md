# T-Shirt Fit Model (Modular, Extensible, Data-Driven)

This project scores t-shirt fits for a given body profile, using your real measurements and a set of tunable, fashion-informed rules. It's **modular**, **configurable**, and ready to scale as you add more garments or new fit criteria.

## Features

- Flexible scoring for multiple fit "aspects" (chest, shoulder, length, hem, sleeve, weight, etc).
- All model logic and tuning centralized in `models/`.
- Clean data IO helpers in `utils/`.
- CLI-friendly script for easy running and CSV output.
- Extensively tested; easily extensible for new fit aspects or garments.
- Type-checked (mypy) and linted (pylint) for code quality.

---

## Directory Structure

tshirt_fit/
├── data/
│ ├── body_measurements.csv # Your body measurements
│ └── shirt_data.csv # All shirt measurements (one row per shirt)
├── models/
│ ├── fit_model.py # Fit scoring and projection logic
│ └── model_params.py # Tunable weights, thresholds, and config
├── utils/
│ └── data_loader.py # Helpers to read and clean CSV files
├── outputs/
│ └── fit_results.csv # Main results output
├── evaluate.py # Entry point script for evaluation
├── requirements.txt # Python dependencies (including mypy/pylint)
├── tests/
│ └── ... # Unit tests and sample data
└── README.md # This file

---

## Data File Format

### `data/body_measurements.csv`

| Measurement      | Value  |
|------------------|--------|
| ChestWidth       | 18.5   |
| ShoulderWidth    | 17.0   |
| TorsoLength      | 27.0   |
| HemWidth         | 18.0   |
| SleeveLength     | 8.0    |

> You can use any set of measurements, but these are the core ones. Extra fields are ignored.

---

### `data/shirt_data.csv`

| ShirtName           | ChestWidth | ShoulderWidth | BodyLength | HemWidth | SleeveLength | Weight |
|---------------------|------------|---------------|------------|----------|--------------|--------|
| Test Tee Regular    | 19.0       | 17.0          | 27.5       | 18.0     | 8.5          | 5.5    |
| Test Tee Boxy       | 21.0       | 19.0          | 25.5       | 21.0     | 9.0          | 6.2    |
| Test Tee Tight      | 17.5       | 16.0          | 26.0       | 17.0     | 7.5          | 4.0    |

- **Column names are case-insensitive and will be normalized.**
- Extra columns are ignored.

---

## Model Overview

- **Fit Score** (0–100) and Confidence are calculated using all available aspects (chest, shoulder, length, hem, sleeve, weight).
- All scoring rules and tunable weights are in `models/model_params.py`.
- You can add or remove aspects by editing the `ASPECTS` and `ASPECT_SCORERS` dictionaries.

---

## How to Run

1. **Prepare your data**
   - Place `body_measurements.csv` and `shirt_data.csv` in the `data/` folder.
   - Make sure the column names match those shown above.

2. **Install dependencies**
   ```sh
   pip install -r requirements.txt
