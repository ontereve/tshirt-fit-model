"""
model_params.py
Centralizes all tunable numeric and structural parameters for t-shirt fit scoring.
Edit here to tweak the fit model globally.
"""

# --- Fit Aspect Definitions & Scoring Setup ---

# Relative weights of each fit aspect, including experimental/inactive ones
WEIGHTS = {
    "chest": 0.20,
    "shoulder": 0.20,
    "length": 0.15,
    "hem": 0.15,
    "sleeve": 0.15,
    "weight": 0.15,
    # 'fabric_stretch': 0.05,   # Example: inactive/experimental aspect
}

# ASPECTS = ordered list of *active* fit aspects currently used for scoring/output.
ASPECTS = ["chest", "shoulder", "length", "hem", "sleeve", "weight"]
# Only aspects listed here are scored; others in WEIGHTS are ignored unless added here.

# Aspects whose scoring needs shirt chest width as a fallback/ratio.
ASPECTS_NEED_CHEST = {"length", "hem", "sleeve"}

ASPECT_SCORERS = {
    "chest": {
        "fields": ("ChestWidth", "ChestWidth"),
        "scorer": "score_chest",
        "weight": WEIGHTS["chest"],
    },
    "shoulder": {
        "fields": ("ShoulderWidth", "ShoulderWidth"),
        "scorer": "score_shoulder",
        "weight": WEIGHTS["shoulder"],
    },
    "length": {
        "fields": ("TorsoLength", "BodyLength"),
        "scorer": "score_length",
        "weight": WEIGHTS["length"],
    },
    "hem": {
        "fields": ("HemWidth", "HemWidth"),
        "scorer": "score_hem",
        "weight": WEIGHTS["hem"],
    },
    "sleeve": {
        "fields": ("SleeveLength", "SleeveLength"),
        "scorer": "score_sleeve",
        "weight": WEIGHTS["sleeve"],
    },
    "weight": {
        "fields": (None, "Weight"),
        "scorer": "score_weight",
        "weight": WEIGHTS["weight"],
    },
    # Add new/experimental aspects here (inactive unless present in ASPECTS)
}


# --- Per-Aspect Scoring Parameters ---

## Chest
CHEST_TOO_TIGHT_PENALTY = 35.0
CHEST_SLIM_PENALTY = 20.0
CHEST_RELAXED_MAX = 2.0  # Inches above body half-chest for "relaxed fit"
CHEST_OVERSIZED_MAX = 4.0  # For "oversized"
CHEST_COMICALLY_OVERSIZED_MAX = 6.0  # Comically oversized above this threshold
CHEST_VERY_OVERSIZED_PENALTY = 10.0

## Shoulder
SHOULDER_TOO_NARROW_PENALTY = 45.0
SHOULDER_DROP_MAX = 2.0  # Inches for drop-shoulder threshold
SHOULDER_VERY_OVERSIZED_PENALTY = 10.0

## Length
LENGTH_CROPPED_MIN = -2  # Cropped if shorter than this below body
LENGTH_SHORT_MAX = -0.5
LENGTH_IDEAL_MAX = 1
LENGTH_LONG_MAX = 3
LENGTH_VERY_LONG_PENALTY = 75

## Hem
HEM_TOO_TIGHT_PENALTY = 60.0
HEM_FLARED_MIN = 2.0
HEM_BOX_CUT_MAX = 1.0
HEM_TAPERED_PENALTY = 70

## Sleeve
SLEEVE_CAP_MIN = -2
SLEEVE_SHORT_MAX = 0
SLEEVE_IDEAL_MAX = 2
SLEEVE_ELBOW_MAX = 2
SLEEVE_CAP_SCORE = 60
SLEEVE_SHORT_SCORE = 80
SLEEVE_IDEAL_SCORE = 100
SLEEVE_ELBOW_SCORE = 85

## Weight (oz)
WEIGHT_LIGHT_MAX = 4.2
WEIGHT_MID_MAX = 5.0
WEIGHT_HEAVY_MAX = 6.5
WEIGHT_VERY_HEAVY_MIN = 6.5
WEIGHT_LIGHT_SCORE = 55
WEIGHT_MID_SCORE = 85
WEIGHT_HEAVY_SCORE = 100
WEIGHT_VERY_HEAVY_SCORE = 90

# --- Interaction Bonuses & Penalties ---
OVERSIZED_HEAVY_BONUS = 7  # If Oversized & Heavyweight (6.0oz+)
OVERSIZED_LIGHT_PENALTY = 6  # Oversized & lightweight (<4.5oz)
RELAXED_HEAVY_BONUS = 3  # Relaxed Fit & heavy (6.5oz+)
SLIM_LIGHT_PENALTY = 4  # Slim Fit & lightweight (<4.5oz)

# --- Bulk Profile Projection Config ---
BULK_PROFILE_CONFIG = {
    "increments": {
        "ChestWidth": 1.0,
        "ShoulderWidth": 0.5,
        "SleeveLength": 0.5,
        "TorsoLength": 0.0,  # Set to nonzero for growth projection
        "HemWidth": 0.5,
        # Add new bulk-related fields here as needed
    },
    "confidence_mod": 0.85,  # Projection confidence modifier
}
