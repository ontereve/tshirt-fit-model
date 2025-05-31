# fit_model.py

import math
from .scorers import *

import logging

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


# --- Adjustments ---
def adjust_for_oversize_weight(tags, shirt_weight, fit_score):
    """
    Adjusts fit_score for oversized/weight interplay.
    """
    if "Comically Oversized" in tags and shirt_weight and shirt_weight < 5.0:
        fit_score = max(0, fit_score - 10)
        logger.info(
            f"Applied harsh penalty for very oversized lightweight shirt (weight: {shirt_weight})."
        )
    elif ("Oversized" in tags or "Very Oversized" in tags) and shirt_weight:
        if shirt_weight >= 6.0:
            fit_score = min(100, fit_score + OVERSIZED_HEAVY_BONUS)
        elif shirt_weight < 4.5:
            fit_score = max(0, fit_score - OVERSIZED_LIGHT_PENALTY * 2)
    if "Relaxed Fit" in tags and shirt_weight and shirt_weight >= 6.5:
        fit_score = min(100, fit_score + RELAXED_HEAVY_BONUS)
    if "Slim Fit" in tags and shirt_weight and shirt_weight < 4.5:
        fit_score = max(0, fit_score - SLIM_LIGHT_PENALTY)
    if "Comically Oversized" in tags and fit_score > 70:
        fit_score = 70
    elif "Very Oversized" in tags and fit_score > 85:
        fit_score = 85
    return fit_score


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
        body_field, shirt_field = config["fields"]
        body_val = get_val(body.get(body_field)) if body_field else None
        shirt_val = get_val(shirt.get(shirt_field)) if shirt_field else None
        scorer_fn = SCORER_FUNCS[config["scorer"]]
        if aspect in ASPECTS_NEED_CHEST:
            # Always pass shirt_chest as third arg
            shirt_chest_val = get_val(shirt.get("ChestWidth"))
            score, tag, rationale = scorer_fn(body_val, shirt_val, shirt_chest_val)
        elif aspect == "weight":
            score, tag, rationale = scorer_fn(shirt_val, scores)
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
    weight_field = ASPECT_SCORERS[weight_aspect]["fields"][1]
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
    for field, inc in BULK_PROFILE_CONFIG["increments"].items():
        if field in new_body and inc:
            new_body[field] = float(new_body[field]) + inc
    return new_body
