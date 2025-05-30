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
   ```

3. **Type-check and lint your code (recommended)**
   ```sh
   mypy .
   pylint models/ utils/ evaluate.py
   ```

4. **Run the main evaluation script**
   ```sh
   python evaluate.py
   ```

5. **View results**
- Results print to the console (pretty table)
- Full details saved to `outputs/fit_results.csv`
- Results are also printed in a clear table in the terminal.

---

# Output

The output CSV includes, for each shirt:

- **FitScore**, **Confidence**, **Tags**, **Rationale**  
- **BulkFitScore**, **BulkConfidence**, **BulkTags**, **BulkRationale** (for projected/“bulked-up” profile)

**Example output:**

```csv
ShirtName,FitScore,Confidence,Tags,Rationale,BulkFitScore,BulkConfidence,BulkTags,BulkRationale
Test Tee Regular,95,83,"Relaxed Fit","Chest: +0.5\" vs body (relaxed).",90,70,"Relaxed Fit","Chest: +0.0\" vs body (relaxed)."
...
```

---

## Extending or Customizing

- **Add or remove fit aspects:**  
  Edit ASPECTS and ASPECT_SCORERS in `models/model_params.py` and add a new scorer function to `fit_model.py`.

- **Change weights or thresholds:**  
  Tune the constants in `model_params.py`.

- **Plug in new garment types:**  
  Add new columns to your CSV and logic to your model as needed.

- **Test everything:**  
  Unit tests live in `tests/` and sample data is provided for reproducibility.

---

## Notes & Best Practices

- **Data Must Be Clean:** Column names *must* match those listed above. Extra columns are ignored.
- **CSV Format:** Google Sheets/Excel can export as CSV. Make sure to save as plain text—avoid Excel formulas in your export.
- **Modular Design:**  
  - Change scoring logic in `models/fit_model.py`.
  - Change or update body/shirt data in your CSVs as needed.
- **Missing Data:**  
  - If any measurement is blank or missing, the script will mark it as such and lower the confidence score automatically.
- **Expanding the Model:**  
  - To add more garment types or measurements, extend `models/fit_model.py` and update your CSV structure accordingly.

---

## Troubleshooting

- **Module not found?**  
  Make sure your folder structure is correct and you’re running the script from your project root (where `main.py` lives).

- **Data not showing up?**  
  Check that your CSV column headers match exactly, and that your data is correctly filled in.

- **Results look off?**  
  Double-check your measurements for typos or errors. Double-check your measurement data and adjust weights/thresholds in model_params.py. You can tweak model weights or logic in `fit_model.py` for more accurate fit scoring.

- **Type or lint errors?**  
  Run mypy or pylint and fix flagged issues for best results.

---

## Code Quality

- This project is regularly checked with mypy (for types) and pylint (for linting).

- All IO is handled in utils/ and the CLI script.

- All fit logic is centralized and modular, making it easy to extend or change.
  
---
