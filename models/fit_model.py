# fit_model.py

import math
import logging
from .scorers import *
from utils.config_loader import load_model_config

MODEL_CONFIG = load_model_config()
ASPECTS = list(MODEL_CONFIG["aspects"].keys())
SCORING_PARAMS = MODEL_CONFIG["scoring_params"]
INTERACTION_ADJUSTMENTS = MODEL_CONFIG["interaction_adjustments"]
PROJECTION_CONFIG = MODEL_CONFIG["projection_config"]

# Extract aspect weights from the config, defaulting to 1 if not present
WEIGHTS = {k: v["weight"] for k, v in MODEL_CONFIG["aspects"].items()}

# Reconstruct ASPECT_SCORERS using config
ASPECT_SCORERS = {
    aspect: {
        "scorer": aspect_cfg["scorer"],
        "body_field": aspect_cfg["body_field"],
        "shirt_field": aspect_cfg["shirt_field"],
        "weight": aspect_cfg["weight"],
        "params": MODEL_CONFIG["scoring_params"].get(aspect, {}),
    }
    for aspect, aspect_cfg in MODEL_CONFIG["aspects"].items()
}

ASPECTS_NEED_CHEST = {
    aspect for aspect, cfg in MODEL_CONFIG["aspects"].items()
    if cfg.get("needs_chest", False)
}

logger = logging.getLogger(__name__)

"""
Fit scoring model for t-shirts.
Calculates a FitScore (0-100) plus confidence, style tags, and a rationale...
"""


# --- Utility Functions ---
def get_val(x):
    """
    Returns None if x is missing, None, or NaN.
    """
    if x is None:
        return None
    if isinstance(x, float) and math.isnan(x):
        return None
    return x


def record_aspect(scores, tags, rationale_parts, missing, aspect, score, tag, rationale):
    scores[aspect] = score
    if tag:
        tags.append(tag)
    if rationale:
        rationale_parts.append(rationale)
    if score == 50:
        missing.append(aspect.capitalize())


def calc_confidence(aspect_present, aspect_count):
    if aspect_count == 0:
        return 0
    return round(100 * aspect_present / aspect_count)


def filter_tags(tags, min_aspects, aspect_present):
    return [t for t in tags if t] if aspect_present >= min_aspects else []


SCORER_FUNCS = {
    "score_chest": score_chest,
    "score_shoulder": score_shoulder,
    "score_length": score_length,
    "score_hem": score_hem,
    "score_sleeve": score_sleeve,
    "score_weight": score_weight,
}


# --- Main Fit/Projection Functions ---
def score_fit(body, shirt):
    """
    Calculates overall t-shirt fit score for a given body and shirt profile.

    Args:
        body (dict): Body measurement data, with expected fields.
        shirt (dict): Shirt measurement data, with expected fields.

    Returns:
        dict: {
            "FitScore": int,
            "Confidence": int,
            "Tags": list of str,
            "Rationale": str
        }
    """
    logger.debug(f"Scoring fit for shirt: {shirt.get('ShirtName', '[unnamed]')}")
    scores, tags, rationale_parts, missing = {}, [], [], []
    aspect_present = 0
    aspect_count = len(ASPECTS)

    for aspect, config in ASPECT_SCORERS.items():
        body_field = config["body_field"]
        shirt_field = config["shirt_field"]
        body_val = get_val(body.get(body_field)) if body_field else None
        shirt_val = get_val(shirt.get(shirt_field)) if shirt_field else None
        scorer_fn = SCORER_FUNCS[config["scorer"]]
        if aspect in ASPECTS_NEED_CHEST:
            # Always pass shirt_chest as third arg
            shirt_chest_val = get_val(shirt.get("ChestWidth"))
            score, tag, rationale = scorer_fn(body_val, shirt_val, shirt_chest_val)
        elif aspect == "weight":
            score, tag, rationale = scorer_fn(shirt_val, scores, ASPECTS)
        else:
            score, tag, rationale = scorer_fn(body_val, shirt_val)
        record_aspect(scores, tags, rationale_parts, missing, aspect, score, tag, rationale)
        if score != 50:
            aspect_present += 1

    # --- Final calculation ---
    fit_score = round(
        sum(scores[aspect] * WEIGHTS[aspect] for aspect in ASPECTS)
        / sum(WEIGHTS[aspect] for aspect in ASPECTS)
    )

    # Get shirt_weight for adjustments (find from shirt or from scores, as in aspect loop)
    # Best option: get directly from the shirt dict using your aspect config:
    weight_aspect = "weight"
    weight_field = ASPECT_SCORERS[weight_aspect]["shirt_field"]
    shirt_weight = get_val(shirt.get(weight_field)) if weight_field else None

    # Oversize & Weight Adjustments
    if aspect_present >= 2:
        fit_score = adjust_for_oversize_weight(tags, shirt_weight, fit_score)

    confidence = calc_confidence(aspect_present, aspect_count)
    tags = filter_tags(tags, 2, aspect_present)

    if aspect_present == 0:
        return {
            "FitScore": "",
            "Confidence": 0,
            "Tags": [],
            "Rationale": "No measurements available for this shirt.",
        }

    return {
        "FitScore": fit_score,
        "Confidence": confidence,
        "Tags": tags,
        "Rationale": " ".join(rationale_parts),
    }


def bulk_projection_profile(body):
    """
    Returns a projected bulked-up body profile based on the provided body measurements.
    """
    logger.debug(f"Generating bulk profile projection from: {body}")
    new_body = body.copy()
    for field, inc in PROJECTION_CONFIG["increments"].items():
        if field in new_body and inc:
            new_body[field] = float(new_body[field]) + inc
    return new_body
