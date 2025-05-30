# README for Modular T-Shirt Fit Model Project

This project is organized for maximum maintainability and clarity. You can use Google Sheets, Excel, or any CSV for input. All logic is separated and swappable.

## Directory structure

```
tshirt_fit/
├── data/
│   ├── body_measurements.csv        # Your body measurements
│   └── shirt_measurements.csv       # All shirt measurements (one row per shirt)
├── models/
│   └── fit_model.py                 # Model logic (see below)
├── utils/
│   ├── data_loader.py               # Helper to read/clean up csv
├── outputs/
│   └── fit_results.csv              # Results output here
├── main.py                          # Entry point script
├── requirements.txt                 # Python requirements
└── README.md                        # This file
```

## Data files

### `data/body_measurements.csv`
```
Measurement,Value
ChestCircumference,37.0
ShoulderWidth,17.4
TorsoLength,15.5
```

### `data/shirt_measurements.csv`
```
ShirtName,ChestWidth,ShoulderWidth,BodyLength
Pepsi Logo Tee,21.12,21.12,28.50
Budweiser Logo (Cropped),20.00,15.50,22.25
Midwest Princess,22.00,19.00,28.75
...
```

## Model
- The model is now **ONLY** chest, shoulder, and length. No sleeve cap, no extra fluff.
- All model weights/tuning live in `models/fit_model.py`.

## How to Run

1. **Prepare your data:**
   - Place your `body_measurements.csv` and `shirt_measurements.csv` files in the `data/` folder. Column headers must match exactly: `ChestCircumference`, `ShoulderWidth`, `TorsoLength` for body; `ShirtName`, `ChestWidth`, `ShoulderWidth`, `BodyLength` for shirts.
2. **Install dependencies:**
   - In your project proj_root, run:
     ```sh
     pip install -r requirements.txt
     ```
3. **Run the main script:**
   - In your project proj_root, run:
     ```sh
     python main.py
     ```
4. **Check your results:**
   - Results print to console and are saved in `outputs/fit_results.csv`.

## Output
- Results in `outputs/fit_results.csv` and on console.

---

## Notes / Things to Keep in Mind

- **Data Must Be Clean:** Column names *must* match those listed above. Extra columns are ignored.
- **CSV Format:** Google Sheets/Excel can export as CSV. You can use either, but never keep Excel formulas in your export.
- **Modular Design:**
   - Change scoring logic in `models/fit_model.py`.
   - Change body data or shirt data in CSVs.
- **Missing Data:**
   - If any field is blank, the script marks it and reduces confidence score automatically.
- **Expanding the Model:**
   - To add more garment types or measurements, adjust code in `models/fit_model.py` and data structure accordingly.

---

## Quick Troubleshooting

- **"Module not found" error:** Make sure your folder structure is correct and you’re running from the project proj_root (where `main.py` lives).
- **Data not showing up:** Check your column headers and make sure you have data in the right columns.
- **Results look off:** Tweak your body measurements or check for typos in your data. Adjust weights or logic in `fit_model.py` as needed.

---

Let me know if you want a zipped copy or any new features!
